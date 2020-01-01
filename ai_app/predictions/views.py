from django.views import generic
from django.views.generic import CreateView
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.template import loader
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required  # 関数用
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin  # クラス用
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from .forms import Photo_form, Login_form, User_update_form, User_create_form
from .models import Photo

# class ~~(LoginRequiredMixin,~~ )
@login_required
def index(request):
    # index
    template = loader.get_template('predictions/index.html')
    context = {'form': Photo_form()}
    return HttpResponse(template.render(context, request))


def predict(request):
    # リザルト表示
    if not request.method == 'POST':
        return redirect('predictions:index')

    form = Photo_form(request.POST, request.FILES)

    if not form.is_valid():
        raise ValueError('invalid form')

    photo = Photo(image=form.cleaned_data['image'])
    predict_label, percentage = photo.predict()
    template = loader.get_template('predictions/result.html')
    context = {
        'image_name': photo.image.name,
        'image_data': photo.image_src(),
        'class_label': predict_label,
        'score': percentage,
    }
    return HttpResponse(template.render(context, request))


class Top(generic.TemplateView):
    template_name = 'predictions/top.html'


class Login(LoginView):
    # ログイン
    form_class = Login_form
    template_name = 'predictions/login.html'

    # def get_success_url(self):
    #    url = self.get_redirect_url()
    #    return url or resolve_url('predictions:predict', pk=self.request.user.pk)


class Logout(LogoutView):
    # ログアウト
    template_name = 'predictions/top.html'

    def log_out(self):
        logout(self.request)


class Only_own_mixin(UserPassesTestMixin, LoginRequiredMixin):
    raise_exception = True

    def test_func(self):
        # 今ログインしてるユーザーのpkと、そのユーザー情報ページのpkが同じか、又はスーパーユーザーなら許可
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


User = get_user_model()


class User_detail(Only_own_mixin, generic.DetailView, LoginRequiredMixin):
    # ユーザ情報閲覧
    model = User
    template_name = 'predictions/user_detail.html'


class User_update(Only_own_mixin, generic.UpdateView, LoginRequiredMixin):
    # ユーザ情報更新
    model = User
    form_class = User_update_form
    template_name = 'predictions/user_update.html'

    def get_success_url(self):
        return resolve_url('predictions:user_detail', pk=self.kwargs['pk'])


class User_create(generic.CreateView):
    # ユーザ仮登録
    template_name = 'predictions/user_create.html'
    form_class = User_create_form

    def form_valid(self, form):
        # 仮登録と本登録用メールの発行.
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単
        # 退会処理も、is_activeをFalseにするだけ
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string(
            'mail_templates/subject.txt', context)
        message = render_to_string(
            'mail_templates/message.txt', context)

        user.email_user(subject, message)
        return redirect('predictions:user_create_done')


class User_create_done(generic.TemplateView):
    # ユーザ仮登録
    template_name = 'predictions/user_create_done.html'


class User_create_complete(generic.TemplateView):
    # メール内URLアクセス後のユーザ本登録
    template_name = 'predictions/user_create_complete.html'
    timeout_seconds = getattr(
        settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        # tokenが正しければ本登録.
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()
