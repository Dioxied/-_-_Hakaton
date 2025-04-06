import {Link} from "react-router-dom";
import styles from "./Navbar.module.css";
const Navbar = () => {
    const logout = () => {
        document.cookie = 'bearer=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
        setAuth(false);
        window.location.reload();
    }
    return (
      <header className={styles.nav_wrapper}>
        <div className={styles.nav_auth}>
            <Link to="/Registration">
                <span>Регистрация</span>
            </Link>

        </div>
        <div className={styles.nav_auth}>
            <Link to="/Authorization">
                <span>Авторизация</span>
            </Link>

        </div>
        <div className={styles.nav_auth}>
            <Link to="/Create">
                <span>Создать чат</span>
            </Link>

        </div>
        <div className={styles.nav_auth}>
            <Link to="/Main">
                <span>Мессенджер</span>
            </Link>

        </div>
        <div className={styles.nav_auth}>
            <Link to="/Rent">
                <span>Биржи, Аренда, Инвестиции</span>
            </Link>

        </div>
        <div className={styles.log_out}>
            <button onClick={logout}>Выйти</button>
        </div>
      </header>

    );
}
export default Navbar