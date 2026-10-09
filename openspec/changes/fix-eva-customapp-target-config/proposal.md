## Why

The Python EVA SDK serializes a `CustomAPP` target configuration at the wrong
JSON level. The service expects `TargetConfig.CustomAPPConfig`, but the SDK
currently sends `TargetConfig.AppID`, so `CreateEvaTask` is rejected with
"CustomAPP Target configuration is missing".

## Change

- Wrap the custom application configuration under `CustomAPPConfig` when
  building `CreateEvaTask` requests.
- Add a regression test for the serialized target configuration.

## Impact

Only the EVA task-creation request payload changes. Existing public method
signatures remain unchanged.
