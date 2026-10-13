#!/usr/bin/env python3
"""Offline behavioral checks; fixtures in memory or test/scratch only."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('subset_tests',
    'line-2/tools/handoff-subset/subset.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Subsets(unittest.TestCase):
    def setUp(self):
        self.files = {'a.txt': b'alpha', 'dir/b.txt': b'beta', 'empty': b'', 'é': b'utf8'}
        self.data = m.WRITER.build(self.files)

    def test_exact_subset_and_own_manifest(self):
        data, result = m.select_bytes(self.data, ['dir/b.txt', 'empty'])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertEqual(set(archive.namelist()), {'HANDOFF.json', 'dir/b.txt', 'empty'})
            self.assertEqual(archive.read('dir/b.txt'), b'beta')
        self.assertEqual(result['omitted_paths'], ['a.txt', 'é'])
        self.assertEqual(result['payload_bytes'], 4)
        self.assertEqual(result['file_count'], 2)
        self.assertEqual(m.WRITER.verify(data)['files'], 2)

    def test_order_independent(self):
        a = m.select_bytes(self.data, ['é', 'a.txt'])
        b = m.select_bytes(self.data, ['a.txt', 'é'])
        self.assertEqual(a, b)

    def test_all_files_reproduce_original(self):
        result, _ = m.select_bytes(self.data, list(self.files))
        self.assertEqual(result, self.data)

    def test_bad_selections(self):
        for paths in ([], ['a.txt', 'a.txt'], ['HANDOFF.json'], ['../a'], ['dir/'],
                      ['/absolute'], ['missing'], ['a.txt*'], ['dir'], [None], 'a.txt'):
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                m.select_bytes(self.data, paths)

    def test_trusted_digest(self):
        _, result = m.select_bytes(self.data, ['empty'], m.WRITER.digest(self.data).upper())
        self.assertTrue(result['source_trusted_digest_matched'])
        for bad in ('no', 'f' * 64):
            with self.assertRaises(ValueError):
                m.select_bytes(self.data, ['empty'], bad)

    def test_tampered_omitted_file_refused(self):
        changed = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.data)) as source, zipfile.ZipFile(changed, 'w') as target:
            for entry in source.infolist():
                content = source.read(entry.filename)
                target.writestr(entry, b'edit' if entry.filename == 'é' else content)
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            m.select_bytes(changed.getvalue(), ['empty'])

    def test_input_budgets(self):
        for limits in (m.INSPECT.Limits(archive_bytes=1),
                       m.INSPECT.Limits(payload_bytes=1), m.INSPECT.Limits(files=1)):
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                m.select_bytes(self.data, ['empty'], limits=limits)

    def test_mutable_input_frozen(self):
        source = bytearray(self.data)
        original = m.WRITER.build
        def mutate(files):
            source[:] = b'changed'
            return original(files)
        m.WRITER.build = mutate
        try:
            data, result = m.select_bytes(source, ['a.txt'])
        finally:
            m.WRITER.build = original
        self.assertEqual(result['source_archive_sha256'], m.WRITER.digest(self.data))
        self.assertEqual(m.WRITER.verify(data)['files'], 1)

    def test_real_archive(self):
        result = m.demo()
        self.assertEqual(result['file_count'], 1)
        self.assertEqual(result['payload_bytes'], 2780)

    def test_path_confinement(self):
        for path in ('../elsewhere.zip', '/tmp/elsewhere.zip'):
            with self.assertRaises(ValueError):
                m.select_path(path, ['a.txt'])
            with self.assertRaises(ValueError):
                m.save_new(path, b'ignored')

    def test_cli_output_and_no_overwrite_or_extraction(self):
        root = Path('test/scratch/handoff-subset')
        root.mkdir(parents=True, exist_ok=True)
        out = root / 'subset.zip'
        if out.exists(): out.unlink()
        args = ['select', 'line-2/handoff.zip', '--file', 'README.md', '--output', str(out)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(m.main(args), 0)
        data = out.read_bytes()
        self.assertEqual(m.WRITER.digest(data), json.loads(stdout.getvalue())['subset_archive_sha256'])
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(m.main(args), 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(out.read_bytes(), data)
        self.assertFalse((root / 'README.md').exists())
        out.unlink()

    def test_symlink_output_refused(self):
        root = Path('test/scratch/handoff-subset')
        root.mkdir(parents=True, exist_ok=True)
        link = root / 'link.zip'
        if link.is_symlink(): link.unlink()
        link.symlink_to('missing.zip')
        try:
            with self.assertRaises(ValueError):
                m.save_new(str(link), b'ignored')
            with self.assertRaises(ValueError):
                m.select_path(str(link), ['README.md'])
        finally:
            link.unlink()
        self.assertFalse((root / 'missing.zip').exists())

    def test_invalid_input_no_output(self):
        out = Path('test/scratch/handoff-subset/invalid.zip')
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = m.main(['select', 'line-2/handoff.zip', '--file', 'absent', '--output', str(out)])
        self.assertEqual(code, 1)
        self.assertFalse(out.exists())
        self.assertEqual(stdout.getvalue(), '')

    def test_cli_real_no_write(self):
        result = subprocess.run([sys.executable, '-B', 'line-2/tools/handoff-subset/subset.py',
                                 'demo'], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['file_count'], 1)
        self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
