import datetime
from . import mixins
from django.shortcuts import redirect, render
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
from .models import Schedule
from .search import scraping, target
from .forms import BS4ScheduleForm, SimpleScheduleForm
import jaconv  # mojimojiの代わり
import re

# class ~~(LoginRequiredMixin,~~ )
@login_required
def predict_home(request):
    # index
    template = loader.get_template('predictions/predict_home.html')
    context = {'form': Photo_form()}
    return HttpResponse(template.render(context, request))


def predict(request):
    # リザルト表示
    if not request.method == 'POST':
        return redirect('predictions:predict_home')

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


def tracking_ship(request):
    track_number = request.GET.get('track_number')
    try:
        if 9 < len(track_number) < 20:  # 10桁以上20桁未満で通す
            track_number = jaconv.z2h(
                track_number, digit=True, ascii=True)  # 全角を半角に
            track_number = re.sub("\\D", "", track_number)  # 数字以外を消す
            texts = scraping(track_number)  # 追跡番号検索
            data_dict = {}  # データ用
            data = {'track_number': str(track_number)}
            for t in target:  # 一度取得データをdictで整形
                data_dict.update([(t, texts[t])])
            target_dict = {  # ターゲット一覧
                target[0]: "日本郵政",
                target[1]: "佐川急便",
                target[2]: "クロネコヤマト",
                target[3]: "西濃運輸",
                target[4]: "日本通運",
                target[5]: "福山通運",
            }
            target_td_num = {
                target[0]: 6,
                target[1]: 8,
                target[2]: 6,
                target[3]: 3,
                target[4]: 5,
                target[5]: 2,
            }
            # for i in range(len(target)):
            #   target_td_num.update([(
            #        target[i], int((len(data_dict[target[i]]))/2)
            #    )])

            data.update([('data', data_dict)])  # 扱いやすい様辞書の入れ子にする
            data.update([('targets', target_dict)])  # ターゲット一覧
            data.update([('td_num', target_td_num)])  # ターゲットのtd数
            # print(data)
            return render(request, 'predictions/search.html', data)
        else:
            return render(request, 'predictions/search.html')
    except:
        return render(request, 'predictions/search.html')


class Index(generic.TemplateView):
    template_name = 'predictions/index.html'


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


User = get_user_model()


class User_detail(generic.DetailView):
    # ユーザ情報閲覧
    model = User
    template_name = 'predictions/user_detail.html'


class User_update(generic.UpdateView):
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


class MonthCalendar(mixins.MonthCalendarMixin, generic.TemplateView):
    """月間カレンダーを表示するビュー"""
    template_name = 'predictions/month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        return context


class WeekCalendar(mixins.WeekCalendarMixin, generic.TemplateView):
    """週間カレンダーを表示するビュー"""
    template_name = 'predictions/week.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_week_calendar()
        context.update(calendar_context)
        return context


class WeekWithScheduleCalendar(mixins.WeekWithScheduleMixin, generic.TemplateView):
    """スケジュール付きの週間カレンダーを表示するビュー"""
    template_name = 'predictions/week_with_schedule.html'
    model = Schedule
    date_field = 'date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_week_calendar()
        context.update(calendar_context)
        return context


class MonthWithScheduleCalendar(mixins.MonthWithScheduleMixin, generic.TemplateView):
    """スケジュール付きの月間カレンダーを表示するビュー"""
    template_name = 'predictions/month_with_schedule.html'
    model = Schedule
    date_field = 'date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        return context


class MyCalendar(mixins.MonthCalendarMixin, mixins.WeekWithScheduleMixin, generic.CreateView):
    """月間カレンダー、週間カレンダー、スケジュール登録画面のある欲張りビュー"""
    template_name = 'predictions/mycalendar.html'
    model = Schedule
    date_field = 'date'
    form_class = BS4ScheduleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        week_calendar_context = self.get_week_calendar()
        month_calendar_context = self.get_month_calendar()
        context.update(week_calendar_context)
        context.update(month_calendar_context)
        return context

    def form_valid(self, form):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(
                year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today()
        schedule = form.save(commit=False)
        schedule.date = date
        schedule.save()
        return redirect('predictions:mycalendar', year=date.year, month=date.month, day=date.day)


class MonthWithFormsCalendar(mixins.MonthWithFormsMixin, generic.View):
    """フォーム付きの月間カレンダーを表示するビュー"""
    template_name = 'predictions/month_with_forms.html'
    model = Schedule
    date_field = 'date'
    form_class = SimpleScheduleForm

    def get(self, request, **kwargs):
        context = self.get_month_calendar()
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        context = self.get_month_calendar()
        formset = context['month_formset']
        if formset.is_valid():
            formset.save()
            return redirect('predictions:month_with_forms')

        return render(request, self.template_name, context)
