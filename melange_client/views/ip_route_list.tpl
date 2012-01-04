%from melange_client.views.helpers import table
{{table.row_view(table.padded_keys(ip_routes).iteritems())}}
%for route in ip_routes:
{{table.row_view(map(lambda (key,value): (route[key], value), table.padded_keys(ip_routes).iteritems()))}}
