## Requirement: CustomAPP task target configuration

### Scenario: Create an evaluation task for a custom application

- **WHEN** `Client.create_task` builds a `CustomAPP` target
- **THEN** the request contains `TargetConfig.CustomAPPConfig`
- **AND** that nested value contains the configured `AppID` and optional
  `ModelAgentConfig`
- **AND** the public `create_task` arguments remain unchanged
