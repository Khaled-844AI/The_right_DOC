let calendar = document.querySelector(".calendar");
const closeModalButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('overlay')
const month_names = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

isLeapYear = (year) => {
  return (
    (year % 4 === 0 && year % 100 !== 0 && year % 400 !== 0) ||
    (year % 100 === 0 && year % 400 === 0)
  );
};

getFebDays = (year) => {
  return isLeapYear(year) ? 29 : 28;
};
let currDate = new Date();

let curr_month = { value: currDate.getMonth() };
let curr_year = { value: currDate.getFullYear() };
const active_year = {value : currDate.getFullYear()}

function showCustomPopup(){

}

overlay.addEventListener('click', () => {
  const modals = document.querySelectorAll('.popup.active')
  modals.forEach(modal => {
    close_popup(modal)
  })
})

function show_popup(popup) {
  if (popup == null) return
  popup.classList.add('active')
  overlay.classList.add('active')
}

function close_popup(popup) {
  if (popup == null) return
  popup.classList.remove('active')
  overlay.classList.remove('active')
}

closeModalButtons.forEach(button => {
  button.addEventListener('click', () => {
    const popup = button.closest('.popup')
    close_popup(popup)
  })
})

generateCalendar = (month, year) => {
  let calendar_days = calendar.querySelector(".calendar-days");
  let calendar_header_year = calendar.querySelector("#year");

  let days_of_month = [
    31,
    getFebDays(year),
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
  ];

  calendar_days.innerHTML = "";

  let currDate = new Date();
  if (!month) month = currDate.getMonth();
  if (!year) year = currDate.getFullYear();

  let curr_month = `${month_names[month]}`;
  month_picker.innerHTML = curr_month;
  calendar_header_year.innerHTML = year;

  // get first day of month

  let first_day = new Date(year, month, 1);

  for (let i = 0; i <= days_of_month[month] + first_day.getDay() - 1; i++) {
    let day = document.createElement("div");
    if (i >= first_day.getDay()) {
      day.classList.add("calendar-day-hover");
      day.innerHTML = i - first_day.getDay() + 1;
      /* day.innerHTML += `<span></span>
                            <span></span>
                            <span></span>
                            <span></span>`; */
      day.addEventListener("click", (event) => {
              const popup = document.querySelector('.popup')
              show_popup(popup , `${year}-${month + 1}-${i - first_day.getDay() + 1}`);
      });
    } else {
      day.classList.add("empty-day");
    }
    calendar_days.appendChild(day);
  }
};

let month_list = calendar.querySelector(".month-list");

let active_date = new Date();

month_names.forEach((e, index) => {
  let month = document.createElement("div");
  month.innerHTML = `<div data-month="${index}">${e}</div>`;
  month.querySelector("div").onclick = (event) => {
    month_list.classList.remove("show");
    let selectedMonth = event.target.dataset.month; // Get the selected month index
    if (curr_year.value > active_year.value)
       generateCalendar(selectedMonth, curr_year.value);
    else if(selectedMonth >= active_date.getMonth())
      generateCalendar(selectedMonth, curr_year.value);
  };
  month_list.appendChild(month);
});


let month_picker = calendar.querySelector("#month-picker");

month_picker.onclick = () => {
  month_list.classList.add("show");
};


generateCalendar(curr_month.value, curr_year.value);

document.querySelector("#prev-year").onclick = () => {

  if (curr_year.value > active_year.value) {
    --curr_year.value;
    generateCalendar(curr_month.value, curr_year.value);
  }
};

document.querySelector("#next-year").onclick = () => {
  ++curr_year.value;
  generateCalendar(curr_month.value, curr_year.value);
};

let dark_mode_toggle = document.querySelector(".dark-mode-switch");

dark_mode_toggle.onclick = () => {
  document.querySelector("body").classList.toggle("light");
  document.querySelector("body").classList.toggle("dark");
};
