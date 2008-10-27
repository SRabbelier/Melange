$(function() {
  var li = $('#side #menu span').parents('li').filter(':has(ul)');
  li.children('a').dblclick(function() {
    window.location = $(this).attr('href');
  }).add(li.children('span')).click(function() {
    $($(this).parents('li')[0]).toggleClass('closed').children("ul").toggle();
    return false;
  });
});
$(function() {
  var li = $('#side #menu span').parents('li').filter(':has(ul)');
  li.children('a').dblclick(function() {
    window.location = $(this).attr('href');
  }).add(li.children('span')).click(function() {
    $($(this).parents('li')[0]).toggleClass('closed').children("ul").toggle();
    return false;
  });
});
$(function() {
  var li = $('#side #menu span').parents('li').filter(':has(ul)');
  li.children('a').dblclick(function() {
    window.location = $(this).attr('href');
  }).add(li.children('span')).click(function() {
    $($(this).parents('li')[0]).toggleClass('closed').children("ul").toggle();
    return false;
  });
});
