# Expose Device Information to MCP Tools

This guide shows how to make the current device ID available to your MCP tools.

## Step 1: Create a custom prompt template

Copy the default `agent-base-prompt.txt` from the `xiaozhi-server` directory into your `data` directory and rename it to `.agent-base-prompt.txt`.

## Step 2: Add `device_id` to the context block

Open `data/.agent-base-prompt.txt`, find the `<context>` section, and add:

```text
- **Device ID:** {{device_id}}
```

After the change, your `<context>` block should look roughly like this:

```text
<context>
[Important: the following information has already been provided in real time. Use it directly instead of calling tools.]
- **Device ID:** {{device_id}}
- **Current time:** {{current_time}}
- **Today's date:** {{today_date}} ({{today_weekday}})
- **Lunar date:** {{lunar_date}}
- **User city:** {{local_address}}
- **7-day local weather:** {{weather_info}}
</context>
```

## Step 3: Point the config at your custom prompt

Open `data/.config.yaml` and find the prompt template setting.

Before:

```yaml
prompt_template: agent-base-prompt.txt
```

After:

```yaml
prompt_template: data/.agent-base-prompt.txt
```

## Step 4: Restart the server

Restart your `xiaozhi-server` instance so the updated prompt template is loaded.

## Step 5: Add a matching MCP parameter

In your MCP method definition, add a parameter with:

- name: `device_id`
- type: `string`
- description: `Device ID`

## Step 6: Test the flow

Wake Xiaozhi again and trigger the MCP method. If the setup is correct, the method will receive the current `device_id`.
