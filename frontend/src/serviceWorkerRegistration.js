// serviceWorkerRegistration.js
export function register() {
  if ('serviceWorker' in navigator) {
    // Eerst alle oude service workers verwijderen
    navigator.serviceWorker.getRegistrations().then(registrations => {
      for (const registration of registrations) {
        registration.unregister();
      }
    }).catch(err => console.error(err));
  }
}

export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then(registration => registration.unregister())
      .catch(error => console.error(error));
  }
}
