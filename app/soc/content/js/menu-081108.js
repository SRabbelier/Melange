$(function() {

   var new_item_text = "(new)"
   $('#menu li.expandable').find('a').each(function(){
     if ($(this).text().indexOf(new_item_text) > -1)
     $(this).css('color', 'red');
   });
   
   $('#side #menu li.expandable > a').dblclick(function() {
    window.location = $(this).attr('href');
  })
  $('#side #menu li.expandable > span').toggle(function() {
    $(this).find("img").attr('src', '/soc/content/images/plus.gif')
    .end().parent().children("ul").toggle();
  }, function() {
    $(this).find("img").attr('src', '/soc/content/images/minus.gif')
    .end().parent().children("ul").toggle();
    return false;
  });
  $('#side #menu li.expandable > span').contents()
  .before('<img src="/soc/content/images/minus.gif" />');
});  
