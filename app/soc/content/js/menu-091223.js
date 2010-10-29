jQuery(function () {
  var new_item_text = "(new)";
  jQuery('#menu li.expandable, #menu li.expandable-collapsed').find('a').each(function () {
    if (jQuery(this).text().indexOf(new_item_text) > -1) {
      jQuery(this).css('color', 'red');
    }
  });

  jQuery('#side #menu li.expandable > a, #side #menu li.expandable-collapsed > a').dblclick(function () {
    window.location = jQuery(this).attr('href');
  });

  var init = function () {
    jQuery('#side #menu li.expandable > span').contents()
    .before('<img src="/soc/content/images/minus.gif" />');

    jQuery('#side #menu li.expandable-collapsed > span').contents()
    .before('<img src="/soc/content/images/plus.gif" />');

    jQuery('#side #menu li.expandable-collapsed > ul').toggle();
  };

  var navbar_toggle = function () {
    var span_object = jQuery(this);
    if (span_object.parent('li:last').hasClass('expandable')) {
      span_object.find('img').attr('src','/soc/content/images/plus.gif').end().parent().children("ul").toggle();
      jQuery(this).parent('li:last').addClass('expandable-collapsed').removeClass('expandable');
    } else {
      span_object.find('img').attr('src','/soc/content/images/minus.gif').end().parent().children("ul").toggle();
      jQuery(this).parent('li:last').addClass('expandable').removeClass('expandable-collapsed');
    }
  };

  jQuery('#side #menu li[class^=expandable] > span').toggle(navbar_toggle, navbar_toggle);

  init();
});
