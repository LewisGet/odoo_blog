from odoo import http
from odoo.http import request
import json


class Regedit(http.Controller):

    @http.route('/hello', type="http", auth='public')
    def hello(self, **kwargs):
        return "hello world"

    @http.route('/display', type='http', auth='public', methods=['GET'])
    def display_content(self, **get):
        request.session.authenticate(get['db'], login=get['username'], password=get['password'])

        try:
            """:type id: int"""
            bid = int(get['id'])

            """@type mod: Orm"""
            mod = http.request.env['orm']
            orm = mod.get()

            orm.execute("select id, content from blog_post where id=%d" % bid)

            contents = [i for i in orm.fetchall()]
            content = (contents[0])[1]

        except Exception as e:
            return str(e)

        return json.dumps(contents)

    @http.route('/get_steam_content', type='http', auth='public', methods=['GET'])
    def get_steam_content(self, **get):
        try:
            import requests as web_request
            from bs4 import BeautifulSoup

            uid = request.session.authenticate(get['db'], login=get['username'], password=get['password'])

            # 預設 cookie 讓他掠過年齡限制
            cookie = self.default_url_arg(get, 'cookie', 'wants_mature_content=1; birthtime=188150401')
            headers = {"Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4"}

            if cookie is not '':
                headers['Cookie'] = cookie

            recieve = web_request.get(get['url'], headers=headers)

            htmlSelector = BeautifulSoup(recieve.content)
            title = htmlSelector.find(id="appHubAppName").text
            main_image = htmlSelector.find(class_="game_header_image_full").get("src")
            discount = htmlSelector.find(class_="discount_pct").text
            countdown = htmlSelector.find(class_="game_purchase_discount_countdown").text

        except Exception as e:
            return str(e)

        htmlContent = """
        <section class="s_picture pt48 pb24 o_cc o_cc2 o_colored_level" data-snippet="s_picture" data-name="Picture" style="background-image: none;">
            <div class="container" style="text-align: center;">
                <h1>{title} {discount}</h1>
                <p>{countdown}</p>
                <p><img src="{main_image}" class="img-thumbnail padding-large" /><br />圖片轉載至 steam</p>
                <p>
                    <a href="{url}">購買網址 Steam</a>
                </p>
            </div>
        </div>
        """.format(title=title, main_image=main_image, discount=discount, countdown=countdown, url=get['url'])

        save = self.default_url_arg(get, "save", False)
        blog_id = int(self.default_url_arg(get, 'blog_id', 3))

        if save == "true":
            try:
                return str(http.request.env['blog.post'].create({
                    'blog_id': blog_id,
                    'name': title + " " + discount,
                    'subtitle': countdown,
                    'content': htmlContent,
                    'website_published': False,
                }))
            except Exception as e:
                return str(e)

        return htmlContent + """<a href="{url}">確認儲存</a>""".format(url=request.httprequest.url + "&save=true")

    def default_url_arg(self, method, index, default):
        try:
            return method[index]
        except:
            return default

    @http.route('/set_steam_url', type="http", auth='public')
    def hello(self, **get):
        uid = request.session.authenticate(get['db'], login=get['username'], password=get['password'])

        try:
            return """
            <form action="/get_steam_content" method="get">
                <p>
                    <span>網址：</span><input type="text" name="url" />
                    <input  type="hidden" name="db" value="{db}" />
                    <input  type="hidden" name="username" value="{username}" />
                    <input  type="hidden" name="password" value="{password}" />
                </p>
                <p>
                    <button type="submit">送出</button>
                </p>
            </form>
            """.format(db=get['db'], username=get['username'], password=get['password'])
        except Exception as e:
            return str(e)
