function BlogPreview(a){this.container_=a}BlogPreview.prototype.show=function(a,b,c,d){a=new google.feeds.Feed(a);var e=this;a.setNumEntries(b);a.load(function(f){e.render_(f,c,d)})};
BlogPreview.prototype.render_=function(a,b,c){if(a.feed&&a.feed.entries){for(;this.container_.firstChild;)this.container_.removeChild(this.container_.firstChild);var d=this.container_;if(!b)b=a.feed.title;if(!c)c=a.feed.link;this.createElement_("h4",d,"","title-section-blog-feed",b);b=this.createDiv_(d,"block-content","block-blog-feed-content");for(var e=0;e<a.feed.entries.length;e++){var f=a.feed.entries[e],g=this.createDiv_(b,"blog-item","blog-feed-item"+e);this.createElement_("span",g,"date","",
(new Date(f.publishedDate)).toDateString());this.createLink_(this.createElement_("span",g,"title"),f.link,f.title)}this.createLink_(this.createDiv_(d,"readmore","block-blog-feed-readmore"),c,"read more")}};BlogPreview.prototype.createDiv_=function(a,b,c,d){return this.createElement_("div",a,b,c,d)};BlogPreview.prototype.createLink_=function(a,b,c){a=this.createElement_("a",a,"","",c);a.href=b;return a};
BlogPreview.prototype.createElement_=function(a,b,c,d,e){a=document.createElement(a);a.id=d;a.className=c;b.appendChild(a);e&&a.appendChild(document.createTextNode(e));return a};