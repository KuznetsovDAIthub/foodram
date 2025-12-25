import React from 'react';
import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const AboutPage = () => {
  return (
    <Main>
      <MetaTags>
        <title>О проекте</title>
        <meta name="description" content="Фудграм - О проекте" />
        <meta property="og:title" content="О проекте" />
      </MetaTags>

      <Container>
        <h1 className={styles.title}>О проекте Foodgram</h1>

        <section className={styles.section}>
          <h2 className={styles.subtitle}>Что такое Foodgram?</h2>
          <p className={styles.text}>
            Foodgram - это онлайн-платформа для обмена рецептами и управления кулинарными коллекциями.
            Проект позволяет пользователям создавать, сохранять и делиться своими рецептами,
            а также находить вдохновение в рецептах других пользователей.
          </p>
        </section>

        <section className={styles.section}>
          <h2 className={styles.subtitle}>Основные возможности</h2>
          <ul className={styles.list}>
            <li>Создание и публикация рецептов</li>
            <li>Подписка на авторов рецептов</li>
            <li>Сохранение избранных рецептов</li>
            <li>Формирование списка покупок</li>
            <li>Управление личным профилем</li>
          </ul>
        </section>

        <section className={styles.section}>
          <h2 className={styles.subtitle}>Функциональность рецептов</h2>
          <ul className={styles.list}>
            <li>Добавление фотографий блюд</li>
            <li>Указание времени приготовления</li>
            <li>Список необходимых ингредиентов</li>
            <li>Пошаговое описание процесса приготовления</li>
            <li>Возможность добавления тегов</li>
          </ul>
        </section>

        <section className={styles.section}>
          <h2 className={styles.subtitle}>Управление подписками</h2>
          <ul className={styles.list}>
            <li>Подписка на интересных авторов</li>
            <li>Лента рецептов от избранных авторов</li>
            <li>Уведомления о новых рецептах</li>
          </ul>
        </section>

        <section className={styles.section}>
          <h2 className={styles.subtitle}>Список покупок</h2>
          <ul className={styles.list}>
            <li>Автоматическое формирование списка ингредиентов</li>
            <li>Возможность скачивания списка покупок</li>
            <li>Отметка о покупке ингредиентов</li>
          </ul>
        </section>

        <section className={styles.section}>
          <h2 className={styles.subtitle}>Административные функции</h2>
          <ul className={styles.list}>
            <li>Модерация контента</li>
            <li>Управление пользователями</li>
            <li>Статистика использования платформы</li>
          </ul>
        </section>
      </Container>
    </Main>
  );
};

export default AboutPage

