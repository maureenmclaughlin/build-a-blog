#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


# def render(self, title, content, error, p):
#     posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC ")
#
#     pagename_label = "<h1>" + "<label>(b)Log: It's Big, It's Heavy, It's Wood.</label>" + "</h1>"
#     post_title_label = "<label>Post title: </label>"
#     post_title_input = "<input type = 'text' name = 'title' value =" + title + ">"
#     post_content_label = "<label>Post content: </label>"
#     post_content_input = "<textarea name = 'content'>" + content + "</textarea>"
#     p = ""
#     submit = "<input type = submit>"
#
#     for p in posts:
#         post_title = Post.title
#         post_content = Post.content

class MainPage(Handler):
    def render_front(self, title = "", content = "", error = ""):
        myPosts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5 OFFSET 0")
        self.render("front.html" , posts = myPosts)
        #self.render("front.html", title = title, content = content, error = error, posts = myPosts)

    def get(self):
        self.render_front()



class PostPage(Handler):
    def render_front(self, title = "", content = "", error = ""):
        self.render("post.html", title = title, content = content, error = error, posts = "")

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            p = Post(title = title, content = content)
            p.put()
            self.redirect("/blog/" + str(p.key().id()))

        else:
            error = "We need both title and content!"
            self.render_front(title, content, error)

class ViewPostHandler(Handler):
    def render_front(self, id, title = "", content = "", error = ""):
        id = int(id)
        data = Post.get_by_id(id)
        post = data
        self.render("permalink.html", title = data.title, content = data.content, error = error, post = post)

    def get(self, id):
        self.render_front(id)


app = webapp2.WSGIApplication([('/blog', MainPage),
                                ('/newpost', PostPage),
                                (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
                                ], debug=True)
