from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django_ratelimit.decorators import ratelimit

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    
    # Блог
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/test/', views.TestBlogView.as_view(), name='test_blog'),
    path('blog/my-posts/', views.UserPostsListView.as_view(), name='user_posts'),
    path('blog/create/', views.UserPostCreateView.as_view(), name='create_post'),
    path('blog/edit/<slug:slug>/', views.UserPostUpdateView.as_view(), name='edit_post'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='post_detail'),
    path('blog/<slug:slug>/comment/<int:comment_id>/reply/', views.CommentReplyView.as_view(), name='comment_reply'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # План питания (бывший VIP раздел)
    path('meal-plan/', views.MealPlanListView.as_view(), name='meal_plan_list'),
    path('meal-plan/calculator/', views.NutritionCalculatorView.as_view(), name='nutrition_calculator'),
    path('meal-plan/goals/', views.NutritionGoalListView.as_view(), name='nutrition_goal_list'),
    path('meal-plan/goals/create/', views.NutritionGoalCreateView.as_view(), name='nutrition_goal_create'),
    path('meal-plan/goals/<int:pk>/', views.NutritionGoalDetailView.as_view(), name='nutrition_goal_detail'),
    path('meal-plan/goals/<int:pk>/edit/', views.NutritionGoalUpdateView.as_view(), name='nutrition_goal_edit'),
    path('meal-plan/goals/<int:pk>/delete/', views.NutritionGoalDeleteView.as_view(), name='nutrition_goal_delete'),
    
    # Управление планами питания
    path('meal-plan/plans/', views.MealPlanListView.as_view(), name='meal_plan_list'),
    path('meal-plan/plans/create/', views.MealPlanCreateView.as_view(), name='meal_plan_create'),
    path('meal-plan/plans/<int:pk>/', views.MealPlanDetailView.as_view(), name='meal_plan_detail'),
    path('meal-plan/plans/<int:pk>/edit/', views.MealPlanUpdateView.as_view(), name='meal_plan_edit'),
    path('meal-plan/plans/<int:pk>/delete/', views.MealPlanDeleteView.as_view(), name='meal_plan_delete'),
    path('meal-plan/plans/<int:plan_id>/add-meal/', views.MealCreateView.as_view(), name='meal_create'),
    path('meal-plan/plans/<int:meal_plan_id>/auto-fill/', views.meal_plan_auto_fill, name='meal_plan_auto_fill'),
    path('meal-plan/plans/meals/<int:pk>/edit/', views.MealUpdateView.as_view(), name='meal_edit'),
    path('meal-plan/plans/meals/<int:pk>/delete/', views.MealDeleteView.as_view(), name='meal_delete'),
    path('meal-plan/plans/meals/<int:meal_id>/add-item/', views.MealItemCreateView.as_view(), name='meal_item_create'),
    path('meal-plan/plans/meal-items/<int:pk>/edit/', views.MealItemUpdateView.as_view(), name='meal_item_edit'),
    path('meal-plan/plans/meal-items/<int:pk>/delete/', views.MealItemDeleteView.as_view(), name='meal_item_delete'),
    
    # Управление продуктами
    path('meal-plan/foods/', views.FoodListView.as_view(), name='food_list'),
    path('meal-plan/foods/create/', views.FoodCreateView.as_view(), name='food_create'),
    path('meal-plan/foods/<int:pk>/edit/', views.FoodUpdateView.as_view(), name='food_edit'),
    path('meal-plan/foods/<int:pk>/delete/', views.FoodDeleteView.as_view(), name='food_delete'),
    path('meal-plan/foods/categories/', views.FoodCategoryListView.as_view(), name='food_category_list'),
    
    # API для плана питания
    path('api/nutrition/calculate/', views.nutrition_calculate_api, name='nutrition_calculate_api'),
    path('api/foods/search/', views.food_search_api, name='food_search_api'),
    path('api/foods/create/', views.food_create_api, name='food_create_api'),
    
    # Сохраненные статьи VIP (для обратной совместимости)
    path('vip/', views.VIPListView.as_view(), name='vip_list'),
    path('vip/create/', views.VIPPostCreateView.as_view(), name='vip_post_create'),
    path('vip/edit/<slug:slug>/', views.VIPPostUpdateView.as_view(), name='vip_post_update'),
    path('vip/delete/<slug:slug>/', views.VIPPostDeleteView.as_view(), name='vip_post_delete'),
    path('vip/<slug:slug>/', views.VIPDetailView.as_view(), name='vip_detail'),
    path('vip/<slug:slug>/comment/<int:comment_id>/reply/', views.VIPCommentReplyView.as_view(), name='vip_comment_reply'),
    path('vip/<slug:slug>/comment/<int:comment_id>/reply-form/', views.VIPCommentReplyFormView.as_view(), name='vip_comment_reply_form'),
    
    # FAQ
    # path('faq/', views.FAQListView.as_view(), name='faq'),
    
    # Рецепты
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    
    # Управление рецептами пользователей
    path('recipes/my-recipes/', views.UserRecipesListView.as_view(), name='user_recipes'),
    path('recipes/create/', views.UserRecipeCreateView.as_view(), name='create_recipe'),
    path('recipes/edit/<slug:slug>/', views.UserRecipeUpdateView.as_view(), name='edit_recipe'),
    path('recipes/delete/<slug:slug>/', views.UserRecipeDeleteView.as_view(), name='delete_recipe'),
    
    # Административные маршруты для рецептов
    path('management/recipes/', views.AdminRecipeListView.as_view(), name='admin_recipe_list'),
    path('management/recipes/edit/<slug:slug>/', views.AdminRecipeUpdateView.as_view(), name='admin_recipe_update'),
    
    # Комментарии к рецептам
    path('recipes/<slug:slug>/comment/<int:comment_id>/reply/', views.RecipeCommentReplyView.as_view(), name='recipe_comment_reply'),
    
    # Детальный просмотр рецепта (должен быть последним в блоке рецептов)
    path('recipes/<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    
    # Вызовы
    path('challenges/', views.ChallengeListView.as_view(), name='challenge_list'),
    path('challenges/<slug:slug>/', views.ChallengeDetailView.as_view(), name='challenge_detail'),
    
    # Профиль пользователя
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.UserProfileDetailView.as_view(), name='user_profile'),
    
    # Калькуляторы
    path('calculators/', views.CalculatorView.as_view(), name='calculators'),
    
    # Поиск
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    
    # Форум
    path('forum/', views.ForumHomeView.as_view(), name='forum_home'),
    path('forum/create-topic/', views.ForumTopicCreateView.as_view(), name='create_topic'),
    path('forum/<slug:category_slug>/create-topic/', views.ForumTopicCreateView.as_view(), name='create_topic_in_category'),
    path('forum/search/', views.ForumSearchView.as_view(), name='forum_search'),
    path('forum/<slug:slug>/', views.ForumCategoryView.as_view(), name='forum_category'),
    path('forum/<slug:category_slug>/<slug:slug>/', views.ForumTopicDetailView.as_view(), name='forum_topic_detail'),
    path('forum/<slug:category_slug>/<slug:topic_slug>/reply/', views.ForumPostCreateView.as_view(), name='create_post_reply'),
    path('forum/post/<int:post_id>/reply/', views.ForumPostReplyView.as_view(), name='forum_post_reply'),
    path('forum/post/<int:post_id>/delete/', views.ForumPostDeleteView.as_view(), name='forum_post_delete'),
    
    # Информационные страницы
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Юридические страницы
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('cookie-policy/', views.CookiePolicyView.as_view(), name='cookie_policy'),
    
    # SEO маршруты
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
    
    # Авторизация и регистрация
    path('login/', ratelimit(key='ip', rate='5/m', block=True)(views.CustomLoginView.as_view()), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', ratelimit(key='ip', rate='3/m', block=True)(views.RegisterView.as_view()), name='register'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='weightloss/auth/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='weightloss/auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    
    # Уведомления
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_as_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/count/', views.get_unread_notifications_count, name='api_notifications_count'),
] 