jQuery(function () {
  var user_preferences = {
    'navbar_structure': {
      'children': []
    }
  };

  var new_item_text = "(new)";
  jQuery('#menu li.expandable, #menu li.expandable-collapsed').find('a').each(function () {
    if (jQuery(this).text().indexOf(new_item_text) > -1) {
      jQuery(this).css('color', 'red');
    }
  });

  jQuery('#side #menu li.expandable > a, #side #menu li.expandable-collapsed > a').dblclick(function () {
    window.location = jQuery(this).attr('href');
  });

  var create_navbar_structure = function (parent_object, child_objects) {
    for (var i = 0; i < child_objects.length; i++) {
      var span_object = jQuery(child_objects[i]);
      var collapsed = span_object.parent('li:last').hasClass('expandable-collapsed') ? true : false;
      var current_object = {
        'span_text': span_object.text(),
        'collapsed': collapsed,
        'children': []
      };
      var current_object_children = span_object.parent().find('span ~ ul > li[class^=expandable] > span');
      if (current_object_children.length !== 0) {
        create_navbar_structure(current_object, current_object_children);
      }
      parent_object.children.push(current_object);
    }
  };

  var setNavbarClasses = function (parent_object, child_objects) {
    for (var i = 0; i < child_objects.length; i++) {
      var span_queue = [];
      if (parent_object.span_text !== undefined) {
        span_queue.push({
          "span_text": parent_object.span_text,
          "collapsed": parent_object.collapsed
        });
      }
      if (child_objects[i].span_text !== undefined) {
        span_queue.push({
          "span_text": child_objects[i].span_text,
          "collapsed": child_objects[i].collapsed
        });
      }
      setNavbarClasses(child_objects[i], child_objects[i].children);
      if (span_queue.length !== 0) {
        var selector = '#side #menu > ul > li > ul > li[class^=expandable]';
        for (var span_queue_index = (span_queue.length - 1); span_queue_index >= 0; span_queue_index--) {
          for (var times = 0; times < span_queue_index; times++) {
            selector += ' > ul > li[class^=expandable]';
          }
          var selected_span = jQuery(selector + ' > span').filter(function () {
            return jQuery(this).html() === span_queue[span_queue_index].span_text;
          })[0];
          if (span_queue[span_queue_index].collapsed) {
            jQuery(selected_span).parent('li:last').addClass('expandable-collapsed').removeClass('expandable');
          } else {
            jQuery(selected_span).parent('li:last').addClass('expandable').removeClass('expandable-collapsed');
          }
        }
      }
    }
  };

  var init = function () {
    var saved_user_preferences = jQuery.cookie("user_preferences");
    try {
      saved_user_preferences = JSON.parse(saved_user_preferences);
      if (saved_user_preferences === null) {
        throw "null_cookie";
      }
      setNavbarClasses(saved_user_preferences.navbar_structure, saved_user_preferences.navbar_structure.children);
    }
    catch (e) {
      jQuery.cookie("user_preferences", {path: '/'});
      var first_level_spans = jQuery('#side #menu > ul > li > ul > li[class^=expandable] > span');
      create_navbar_structure(user_preferences["navbar_structure"], first_level_spans);
      jQuery.cookie("user_preferences",JSON.stringify(user_preferences),{path:'/', expires: 14});
    }
    openCloseMenu();
  };

  var openCloseMenu = function () {
    jQuery('#side #menu li.expandable > span').contents()
    .before('<img src="/soc/content/images/minus.gif" />');

    jQuery('#side #menu li.expandable-collapsed > span').contents()
    .before('<img src="/soc/content/images/plus.gif" />');

    jQuery('#side #menu li.expandable-collapsed > ul').hide();
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
    var first_level_spans = jQuery('#side #menu > ul > li > ul > li[class^=expandable] > span');
    create_navbar_structure(user_preferences["navbar_structure"], first_level_spans);
    jQuery.cookie("user_preferences",JSON.stringify(user_preferences),{path:'/', expires: 14});
  };

  jQuery('#side #menu li[class^=expandable] > span').toggle(navbar_toggle, navbar_toggle);

  init();
});
