import React from 'react';
import { Title, Container, Main } from '../../components';
import styles from './styles.module.css';
import MetaTags from 'react-meta-tags';

const TechnologiesPage = () => {
  return (
    <Main>
    <MetaTags>
        <title>Технологии</title>
      <meta name="description" content="Фудграм - Технологии" />
        <meta property="og:title" content="Технологии" />
    </MetaTags>
    
    <Container>
        <h1 className={styles.title}>Технологии проекта</h1>

        <div className={styles.techGrid}>
          <section className={styles.techCard}>
            <h2 className={styles.techTitle}>Backend</h2>
            <div className={styles.techContent}>
              <h3 className={styles.techSubtitle}>Python</h3>
              <p className={styles.techDescription}>
                Основной язык программирования для разработки серверной части приложения
              </p>
              <ul className={styles.techList}>
                <li>Django REST framework</li>
                <li>PostgreSQL</li>
                <li>Django ORM</li>
                <li>JWT Authentication</li>
              </ul>
            </div>
          </section>

          <section className={styles.techCard}>
            <h2 className={styles.techTitle}>Frontend</h2>
            <div className={styles.techContent}>
              <h3 className={styles.techSubtitle}>React</h3>
              <p className={styles.techDescription}>
                Современный JavaScript-фреймворк для создания пользовательского интерфейса
              </p>
              <ul className={styles.techList}>
                <li>React Router</li>
                <li>CSS Modules</li>
                <li>Context API</li>
                <li>React Hooks</li>
              </ul>
            </div>
          </section>

          <section className={styles.techCard}>
            <h2 className={styles.techTitle}>DevOps</h2>
            <div className={styles.techContent}>
              <h3 className={styles.techSubtitle}>Docker</h3>
              <p className={styles.techDescription}>
                Контейнеризация и оркестрация приложения
              </p>
              <ul className={styles.techList}>
                <li>Docker Compose</li>
                <li>Nginx</li>
                <li>GitHub Actions</li>
                <li>CI/CD</li>
            </ul>
          </div>
          </section>
        </div>
    </Container>
  </Main>
  );
};

export default TechnologiesPage;

