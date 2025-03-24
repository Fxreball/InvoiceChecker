import './Header.css';
import logo from '../images/logo.png'; // Zorg ervoor dat het pad naar je logo correct is

export default function Header() {
  return (
    <header className="header">
      <img src={logo} alt="Logo" className="logo" />
    </header>
  );
}