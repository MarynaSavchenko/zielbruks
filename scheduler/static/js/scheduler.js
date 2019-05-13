function setupCalendar(events, start_date) {

  var nav = new DayPilot.Navigator("nav");
  nav.showMonths = 2;
  nav.selectMode = "day";
  nav.startDate = start_date;
  nav.onTimeRangeSelected = function (args) {
    dp.startDate = args.start;
    dp.update();
  };
  nav.init();

  var dp = new DayPilot.Calendar("dp");
  dp.startDate = start_date;
  dp.viewType = "Days";
  dp.days = 2;
  dp.businessBeginsHour = 7;
  dp.events.list = events;
  dp.eventClickHandling = "Enabled";
  dp.eventMoveHandling = "Disabled";
  dp.eventResizeHandling = "Disabled";
  dp.onEventClicked = function (args) {
    document.getElementById("details").innerText = args.e.text();
  };

  dp.init();
  return dp;
}

function setupEditButton(daypilot, url) {
  daypilot.onEventClicked = function (args) {
    document.getElementById("details").innerText = args.e.text();

    var old_btn = document.getElementById('edit_button');
    old_btn.parentNode.removeChild(old_btn);

    var new_btn = document.createElement("button");
    new_btn.setAttribute("id", "edit_button");
    new_btn.setAttribute("class", "edit btn btn-primary");
    new_btn.innerHTML = "Edit event";
    document.getElementById('p_with_buttons').appendChild(new_btn);
    $('#edit_button').show();
    $("#edit_button").modalForm({ formURL: url.replace(/123/, args.e.id()) });
  };
}
