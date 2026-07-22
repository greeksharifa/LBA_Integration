import configparser
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).parents[1]


class RepositoryDependencyTest(unittest.TestCase):
    def test_scene_graph_generator_is_a_pinned_submodule(self):
        config = configparser.ConfigParser()
        config.read(ROOT / ".gitmodules")
        section = 'submodule "cross-graph-attention"'

        self.assertIn(section, config)
        self.assertEqual(config[section]["path"], "cross-graph-attention")
        self.assertEqual(
            config[section]["url"],
            "https://github.com/youngyoung1021/cross-graph-attention.git",
        )

        output = subprocess.check_output(
            ["git", "ls-files", "-s", "cross-graph-attention"],
            cwd=ROOT,
            text=True,
        )
        self.assertTrue(output.startswith("160000 "))

    def test_tracked_configuration_has_no_old_checkout_path(self):
        path = ROOT / "LBA_SIMPLE_LAVIS/projects/LBA/eval/DramaQA_eval_sq_finetune.yaml"

        source = path.read_text()
        self.assertNotIn("/home/", source)
        self.assertIn('finetuned: "lavis/z_output_ckpt/', source)


if __name__ == "__main__":
    unittest.main()
