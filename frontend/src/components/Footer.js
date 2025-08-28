import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className='footer'>
      <span>&copy; {currentYear} - Owen Coenraad</span>
    </footer>
  );
};

export default Footer;
