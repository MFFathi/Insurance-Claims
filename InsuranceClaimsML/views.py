from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import MLModel
from .forms import MLModelForm

class MLModelListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MLModel
    template_name = 'ml/model_list.html'
    context_object_name = 'models'
    
    def test_func(self):
        return self.request.user.check_permission('ml.view')

class MLModelUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MLModel
    form_class = MLModelForm
    template_name = 'ml/model_form.html'
    success_url = reverse_lazy('ml:model_list')
    
    def test_func(self):
        return self.request.user.check_permission('ml.upload')
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'ML Model uploaded successfully!')
        return super().form_valid(form)

class MLModelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MLModel
    form_class = MLModelForm
    template_name = 'ml/model_form.html'
    success_url = reverse_lazy('ml:model_list')
    
    def test_func(self):
        return self.request.user.check_permission('ml.update')
    
    def form_valid(self, form):
        messages.success(self.request, 'ML Model updated successfully!')
        return super().form_valid(form)

class MLModelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MLModel
    template_name = 'ml/model_confirm_delete.html'
    success_url = reverse_lazy('ml:model_list')
    
    def test_func(self):
        return self.request.user.check_permission('ml.update')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'ML Model deleted successfully!')
        return super().delete(request, *args, **kwargs) 