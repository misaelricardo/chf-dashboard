function toggleDropdown(button) {
  const dropdown = button.nextElementSibling;

  // Close all other dropdowns
  document.querySelectorAll(".dropdown-menu").forEach(menu => {
    if (menu !== dropdown) {
      menu.classList.add("hidden");
    }
  });

  // Toggle the clicked one
  dropdown.classList.toggle("hidden");
}

// Close dropdown when clicking outside
document.addEventListener("click", function (event) {
  const isDropdownButton = event.target.closest("[onclick='toggleDropdown(this)']");
  const isDropdownMenu = event.target.closest(".dropdown-menu");

  // If not clicking the button or dropdown, hide all
  if (!isDropdownButton && !isDropdownMenu) {
    document.querySelectorAll(".dropdown-menu").forEach(menu => {
      menu.classList.add("hidden");
    });
  }
});
