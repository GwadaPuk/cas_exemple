const profile = document.createElement("p");
const button = document.createElement("a");

let response = await fetch("/data");
let res = await response.json();

if ('username' in res) {
    profile.textContent = 'Vous êtes connecté en tant qu\'utilisateur : ' + res['username'];
    button.href = "/logout";
    button.textContent = 'Se déconnecter';
} else {
    profile.textContent = 'Vous n\'êtes pas connecté';
    button.href = "/login";
    button.textContent = 'Se connecter';
}

document.body.appendChild(profile);
document.body.appendChild(button);