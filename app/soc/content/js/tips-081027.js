$(function() {
  // Change 'title' to something else first
  $('tr[title]').each(function() {
    $(this).attr('xtitle', $(this).attr('title')).removeAttr('title');
  })
    .children().children(':input')
      // Set up event handlers
      .bt({trigger: ['helperon', 'helperoff'],
             titleSelector: "parent().parent().attr('xtitle')",
             killTitle: false,
             fill: 'rgba(135, 206, 250, .9)',
             positions: ['bottom', 'top', 'right']
          })
      .bind('focus', function() {
                $(this).trigger('helperon');
              })
      .bind('blur', function() {
                $(this).trigger('helperoff');
              })
    .parent()
      .bind('mouseover', function() {
                $(this).children(':input').trigger('helperon');
              })
      .bind('mouseleave', function() {
                $(this).children(':input').trigger('helperoff');
              });
});

