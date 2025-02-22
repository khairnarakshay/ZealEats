from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    #path('home/', views.dashboard_home, name='vendor_home'),
    #path('admin/logout/',views.admin_logout, name='admin_logout'),  # Custom admin logout
    path('login/', views.vendor_login, name='login'),
    path('logout/', views.vendor_logout, name='logout'),
    path('register/', views.register_view, name='register'),  # New registration URL
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/', views.order, name='order'),
    path('additems/', views.additems, name='additems'),
    path('manage-items/', views.manage_items, name='manage_items'),
    path("update-items/<int:id>",views.update_items, name="update-item"),
    
    path("delete-item/<int:item_id>/", views.delete_item, name="delete-item"),
    path('account/', views.account, name='account'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
