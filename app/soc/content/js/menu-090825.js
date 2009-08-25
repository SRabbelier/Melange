jQuery(function () {
  var new_item_text = "(new)";
  jQuery('#menu li.expandable').find('a').each(function () {
    if (jQuery(this).text().indexOf(new_item_text) > -1) {
      jQuery(this).css('color', 'red');
    }
  });

  jQuery('#side #menu li.expandable > a').dblclick(function () {
    window.location = jQuery(this).attr('href');
  });

  jQuery('#side #menu li.expandable > span').toggle(function () {
    jQuery(this).find("img").attr('src', '/soc/content/images/plus.gif')
    .end().parent().children("ul").toggle();
  }, function () {
    jQuery(this).find("img").attr('src', '/soc/content/images/minus.gif')
    .end().parent().children("ul").toggle();
    return false;
  });

  jQuery('#side #menu li.expandable > span').contents()
  .before('<img src="/soc/content/images/minus.gif" />');
});
