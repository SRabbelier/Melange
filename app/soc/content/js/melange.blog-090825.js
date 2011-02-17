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

BlogPreview.prototype.show = function (url, entries_num, title, title_link) {
  var feed = new google.feeds.Feed(url);
  var preview = this;
  feed.setNumEntries(entries_num);
  feed.load(function (result) {
    preview.render_(result, title, title_link);
  });
};

BlogPreview.prototype.render_ = function (result, title, title_link) {
  if (!result.feed || !result.feed.entries) {
    return;
  }
  while (this.container_.firstChild) {
    this.container_.removeChild(this.container_.firstChild);
  }

  var container = this.container_;
  if (!title) {
    title = result.feed.title;
  }
  if (!title_link) {
    title_link = result.feed.link;
  }
  this.createElement_("h4", container, "", "title-section-blog-feed", title);

  var blog = this.createDiv_(container, "block-content",
                             "block-blog-feed-content");
  for (var i = 0; i < result.feed.entries.length; i++) {
    var entry = result.feed.entries[i];
    var div = this.createDiv_(blog, "blog-item", "blog-feed-item"+i);
    var publishedDate = new Date(entry.publishedDate);
    this.createElement_("span", div, "date", "", publishedDate.toDateString());
    var linkDiv = this.createElement_("span", div, "title");
    this.createLink_(linkDiv, entry.link, entry.title);
  }
  var footer = this.createDiv_(container, "readmore",
                               "block-blog-feed-readmore");
  this.createLink_(footer, title_link, "read more");
};

BlogPreview.prototype.createDiv_ = function (parent, className,
                                             idName, opt_text) {
  return this.createElement_("div", parent, className, idName, opt_text);
};

BlogPreview.prototype.createLink_ = function (parent, href, text) {
  var link = this.createElement_("a", parent, "", "", text);
  link.href = href;
  return link;
};

BlogPreview.prototype.createElement_ = function (tagName, parent, className,
                                                 idName, opt_text) {
  var div = document.createElement(tagName);
  div.id = idName;
  div.className = className;
  parent.appendChild(div);
  if (opt_text) {
    div.appendChild(document.createTextNode(opt_text));
  }
  return div;
};
