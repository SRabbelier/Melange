/* Copyright 2008 the Melange authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *   http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

function BlogPreview(container) {
  this.container_ = container;
}

BlogPreview.prototype.show = function(url, title, title_link) {
  var feed = new google.feeds.Feed(url);
  var preview = this;
  feed.load(function(result) {
    preview.render_(result, title, title_link);
  });
}

BlogPreview.prototype.render_ = function(result, title, title_link) {
  if (!result.feed || !result.feed.entries) return;
  while (this.container_.firstChild) {
    this.container_.removeChild(this.container_.firstChild);
  }

  var blog = this.createDiv_(this.container_, "blog");
  var header = this.createElement_("h2", blog, "");
  if (!title) {
    title = result.feed.title;
  }
  if (!title_link) {
    title_link = result.feed.link;
  }
  this.createLink_(header, title_link, title);

  for (var i = 0; i < result.feed.entries.length; i++) {
    var entry = result.feed.entries[i];
    var div = this.createDiv_(blog, "entry");
    var linkDiv = this.createDiv_(div, "title");
    this.createLink_(linkDiv, entry.link, entry.title);
    if (entry.author) {
      this.createDiv_(div, "author", "Posted by " + entry.author);
    }
    this.createDiv_(div, "snippet", entry.contentSnippet);
  }
}

BlogPreview.prototype.createDiv_ = function(parent, className, opt_text) {
  return this.createElement_("div", parent, className, opt_text);
}

BlogPreview.prototype.createLink_ = function(parent, href, text) {
  var link = this.createElement_("a", parent, "", text);
  link.href = href;
  return link;
}

BlogPreview.prototype.createElement_ = function(tagName, parent, className,
                                                opt_text) {
  var div = document.createElement(tagName);
  div.className = className;
  parent.appendChild(div);
  if (opt_text) {
    div.appendChild(document.createTextNode(opt_text));
  }
  return div;
}

