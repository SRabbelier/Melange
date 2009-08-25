jQuery(
  function () {
    jQuery('.datetime-pick').datetimepicker();
    jQuery('.date-pick').datetimepicker({
      'pickDateOnly': true,
      'defaultDate': new Date('01/01/1974'),
      'timeFormat': '',
      'yearRange': '1900:2008'
    });
  }
);

