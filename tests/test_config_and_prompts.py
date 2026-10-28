from pathlib import Path

import pytest
from jinja2 import UndefinedError
from pydantic import ValidationError

from eval_engine.config import REPO_ROOT, load_config
from eval_engine.prompts import PromptRegistry
from tests.conftest import make_config


def test_repo_config_is_valid() -> None:
    config = load_config()
    assert {"generator", "judge", "verifier", "amendment_proposer"} <= set(config.roles)
    # Design invariant: judge and verifier come from a different provider than the generator.
    family = {name: role.family for name, role in config.roles.items()}
    assert family["judge"] != family["generator"]
    assert family["verifier"] != family["generator"]
    assert family["verifier"] != family["amendment_proposer"]
    assert family["verifier"] != family["judge"]


def test_unknown_provider_in_role_rejected() -> None:
    with pytest.raises(ValidationError, match="unknown provider"):
        make_config(
            roles={
                "judge": {
                    "provider": "nope",
                    "model": "x",
                    "family": "x",
                    "temperature": 0,
                    "max_output_tokens": 1,
                }
            }
        )


def test_weights_sum_to_one() -> None:
    import yaml

    weights = yaml.safe_load((REPO_ROOT / "config" / "weights.yaml").read_text())
    for task_type, row in weights.items():
        assert abs(sum(row.values()) - 1.0) < 1e-9, task_type


def test_prompt_render_and_hash() -> None:
    p = PromptRegistry().render("smoke", {"token": "abc"})
    assert p.version == 1 and "abc" in p.user and len(p.template_hash) == 64


def test_missing_variable_is_an_error() -> None:
    with pytest.raises(UndefinedError):
        PromptRegistry().render("smoke", {})


def test_prompt_name_must_match_file(tmp_path: Path) -> None:
    (tmp_path / "a.yaml").write_text("name: b\nversion: 1\nsystem: s\nuser: u\n")
    with pytest.raises(ValueError, match="declares name"):
        PromptRegistry(tmp_path).get("a")


def test_model_limit_overrides() -> None:
    config = make_config(
        providers={
            "alpha": {
                "api_key_env": None,
                "limits": {"rpd": 20},
                "model_limits": {"lite": {"rpd": 500}},
            }
        }
    )
    p = config.providers["alpha"]
    assert p.limits_for("lite").rpd == 500
    assert p.limits_for("anything-else").rpd == 20
