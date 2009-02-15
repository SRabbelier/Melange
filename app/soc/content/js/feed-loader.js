google.load("feeds", "1");

function initialize() {
  var blog = new BlogPreview(document.getElementById("blog"));
  blog.show("{{ entity.feed_url }}", 3);
}
google.setOnLoadCallback(initialize);

