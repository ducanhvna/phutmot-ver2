from odoo import http

class MyController(http.Controller):

    @http.route('/get_csrf_token', type='http', auth='public', csrf=False)
    def get_csrf_token(self):
        csrf_token = http.request.csrf_token()
        return http.Response(status=200, content_type='application/json', response=str(csrf_token))

    @http.route('/my_endpoint', type='json', methods=['POST'], csrf=False)
    def my_method(self, data=None):
        return data
