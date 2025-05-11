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
    path('admin/statistics/', views.admin_statistics, name='admin_statistics'),
    path('admin/statistics-offline/', views.admin_statistics_offline, name='admin_statistics_offline'),
    #path('order/', views.order, name='order'),
    path('additems/', views.additems, name='additems'),
    path('manage-items/', views.manage_items, name='manage_items'),
    # path("update-items/<int:id>",views.update_items, name="update-item"),
    path('update-item/<int:id>/', views.update_items, name='update-item'),
    
    path("delete-item/<int:item_id>/", views.delete_item, name="delete-item"),
    path('mark-out-of-stock/<int:item_id>/', views.mark_out_of_stock, name='mark-out-of-stock'),
    path('mark-in-stock/<int:item_id>/', views.mark_in_stock, name='mark-in-stock'),
    path('account/', views.vendor_update_profile, name='account'),
    path('update-order-status/<int:order_id>/',views.update_order_status, name='update-order-status'),
   # path('admin/statistics/pdf/', views.generate_statistics_pdf, name='generate_statistics_pdf'),
    path('download/statistics/pdf/', views.download_statistics_pdf, name='download_statistics_pdf'),
    path('download_excel_report', views.download_excel_report, name='download_excel_report'),
    path('offline-order/', views.create_offline_order, name='create_offline_order'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
