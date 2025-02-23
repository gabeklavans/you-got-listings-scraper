settingsForm = document.forms["settings"];
settingsForm.addEventListener(
  "submit",
  (event) => {
    const formData = new FormData(
      settingsForm,
      document.querySelector("button[value=Save]"),
    );
    for (const [key, value] of formData) {
      console.log(`${key}: ${value}`);
      switch (key) {
        case "BedsMin":
          break;

        default:
          break;
      }
    }

    event.preventDefault();
  },
  false,
);
