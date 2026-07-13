# Deferred docstring-audit ledger

Stale documentation noticed on code that is NOT used by the tutorials or
the stock global-fit pipelines. Per the sprint decision (2026-07-12),
these are NOT fixed during the tutorial overhaul — this list seeds the
later docs pass.

Format: `- <import path or file> — <what is stale> (<who noticed, when>)`

- `lisatools.diagnostic` module docstrings (`inner_product`, `residual_source_likelihood_term`, `data_signal_source_likelihood_term`, ...) — the ``.. math::`` blocks use invalid escape sequences (`\langle`, `\int`, `\ \ `) mixing single and double backslashes, which raise `SyntaxWarning` at import and render wrong in Sphinx. Should become raw docstrings (`r"""`) with consistent single backslashes. Not API drift, so left for the docs pass. (tutorials 02/03 author, 2026-07-12)
- `lisatools.sensitivity` stock matrices `AET2SensitivityMatrix`, `AE1SensitivityMatrix`, `AE2SensitivityMatrix`, `LISASensSensitivityMatrix` — class docstrings still say `Args: f: Frequency array` but the first arg is now `settings: DomainSettingsBase`. The XYZ family (`XYZ1/XYZ2`) + `AET1` + `SensitivityMatrix` + `get_sensitivity` were corrected during the tutorial pass; these AE/T variants are not tutorial-taught (workshop defaults to XYZ). (tutorials 02/03 author, 2026-07-12)
- RESOLVED: `LISASensSensitivityMatrix` (listed in the previous bullet) is now tutorial-taught (further-track `X3` uses it for the single-channel LISASens likelihood), so its `f: Frequency array` docstring was corrected in-tree to `settings: ...` per the docstring-currency rule. The remaining AE/T matrix variants stay deferred (still not tutorial-taught). (further-track X1/X3 author, 2026-07-12)
