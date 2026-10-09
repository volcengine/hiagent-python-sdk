## Context

`hiagent_eva.Client.create_task` creates a `CustomAPP` target. The EVA API
models target configuration as a wrapper containing the type-specific
configuration. The Java SDK already emits this shape through
`EvaTargetConfig.CustomAPPConfig`.

## Decision

Keep `EvaTargetCustomAPPConfig` as the inner configuration model and pass its
serialized value as:

```python
TargetConfig={"CustomAPPConfig": custom_app_cfg}
```

This is the smallest compatible change and does not alter the public Python
API.

## Verification

Use an offline unit test with a capturing EVA service to assert the final
request model. Run the EVA package tests and package build; live API testing is
optional and requires valid credentials and dataset parameters.
