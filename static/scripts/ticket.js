const ticket = document.createElement("p");
const button = document.createElement("a");

let response = await fetch("/data");
let res = await response.json();

console.log(res);

if ('username' in res) {
    ticket.textContent = 'Votre ticket est : ' + res['ticket'];
    button.href = "/logout";
    button.textContent = 'Se déconnecter';
} else {
    ticket.textContent = 'Vous n\'êtes pas connecté';
    button.href = "/login?next=ticket";
    button.textContent = 'Se connecter';
}
document.body.appendChild(ticket);
document.body.appendChild(button);