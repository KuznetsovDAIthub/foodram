import React, { useState } from "react";
import { useTags } from './index.js'
import api from '../api'

export default function useRecipes() {
  const [recipes, setRecipes] = useState([])
  const [recipesCount, setRecipesCount] = useState(0)
  const [recipesPage, setRecipesPage] = useState(1)
  const { value: tagsValue, handleChange: handleTagsChange, setValue: setTagsValue } = useTags()

  const handleLike = ({ id, toLike = true }) => {
    const method = toLike ? api.addToFavorites.bind(api) : api.removeFromFavorites.bind(api)
    method({ id }).then(res => {
      // Проверяем, находимся ли мы на странице избранного
      const isFavoritesPage = window.location.pathname === '/favorites'

      if (isFavoritesPage && !toLike) {
        // На странице избранного при удалении - фильтруем рецепт из списка
        const recipesUpdated = recipes.filter(recipe => recipe.id !== id)
        setRecipes(recipesUpdated)
        setRecipesCount(prevCount => prevCount - 1)
      } else {
        // На других страницах или при добавлении в избранное - только обновляем статус
        const recipesUpdated = recipes.map(recipe => {
          if (recipe.id === id) {
            recipe.is_favorited = toLike
          }
          return recipe
        })
        setRecipes(recipesUpdated)
      }
    })
      .catch(err => {
        const { errors } = err
        if (errors) {
          alert(errors)
        }
      })
  }

  const handleAddToCart = ({ id, toAdd = true, callback }) => {
    const method = toAdd ? api.addToOrders.bind(api) : api.removeFromOrders.bind(api)
    method({ id }).then(res => {
      const recipesUpdated = recipes.map(recipe => {
        if (recipe.id === id) {
          recipe.is_in_shopping_cart = toAdd
        }
        return recipe
      })
      setRecipes(recipesUpdated)
      callback && callback(toAdd)
    })
      .catch(err => {
        const { errors } = err
        if (errors) {
          alert(errors)
        }
      })
  }

  return {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    handleLike,
    handleAddToCart,
    handleTagsChange,
    setTagsValue
  }
}
