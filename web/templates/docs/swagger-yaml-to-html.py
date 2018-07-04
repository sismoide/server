#!/usr/bin/python
"""
Usage:
    
    python swagger-yaml-to-html.py < /path/to/api.yaml > doc.html

"""
import json
import sys

import yaml

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    {%% load static %%}
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Source+Code+Pro:300,600|Titillium+Web:400,600,700"
          rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="{%% static "swagger-ui.css" %%}">
  
  <style>
    html
    {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    *,
    *:before,
    *:after
    {
      box-sizing: inherit;
    }

    body {
      margin:0;
      background: #fafafa;
    }
  </style>
</head>
<body>

<div id="swagger-ui"></div>

<script src="{%% static "swagger-ui-bundle.js" %%}"> </script>
<script src="{%% static "swagger-ui-standalone-preset.js" %%}"> </script>
<script>
window.onload = function() {

  var spec = %s;

  // Build a system
  const ui = SwaggerUIBundle({
    spec: spec,
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout"
  })

  window.ui = ui
}
</script>
</body>

</html>
"""
spec = yaml.load(sys.stdin)
sys.stdout.write(TEMPLATE % str(json.dumps(spec, ensure_ascii=False)))
