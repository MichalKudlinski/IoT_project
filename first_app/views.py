from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm, UserRegisterForm
from .models import Conversation, Message


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('conversation_redirect')
    else:
        form = UserRegisterForm()
    return render(request, 'chat/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('conversation_redirect')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)


    messages = conversation.messages.all().order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()

            # Redirect back to chat_view to render updated messages
            return redirect('chat_view', conversation_id=conversation_id)
    else:
        form = MessageForm()

    return render(request, 'chat/chat.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form,
    })
@login_required
def send_message(request):
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        content = request.POST.get('content')

        conversation = get_object_or_404(Conversation, id=conversation_id)


        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            content=content
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@login_required
def conversation_redirect(request):
    user_conversations = Conversation.objects.filter(participants=request.user)

    if request.method == 'POST':
        option = request.POST.get('option')

        if option == 'new':
            # Create a new conversation
            return redirect('create_conversation')
        elif option == 'join':
            conversation_id = request.POST.get('conversation_id')

            try:
                conversation = Conversation.objects.get(id=conversation_id)

                conversation.participants.add(request.user)
                return redirect('chat_view', conversation_id=conversation_id)

            except Conversation.DoesNotExist:
                messages.error(request, f'Conversation {conversation_id} does not exist.')
                return redirect('conversation_redirect')

    context = {
        'user_conversations': user_conversations,
    }
    return render(request, 'chat/conversation_redirect.html', context)



@login_required
def fetch_messages(request, username):
    other_user = get_object_or_404(User, username=username)

    # Retrieve the conversation between request.user and other_user
    conversation = Conversation.objects.filter(participants=request.user).annotate(num_participants=Count('participants')).filter(num_participants=2).get(participants=other_user)

    messages = conversation.messages.all().order_by('timestamp')

    messages_data = [{
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'timestamp': message.timestamp
    } for message in messages]

    return JsonResponse({'messages': messages_data})

@login_required
def create_conversation(request):
    if request.method == 'POST':
        other_username = request.POST.get('other_username')
        try:
            other_user = User.objects.get(username=other_username)
            if other_user == request.user:
                return render(request, 'chat/create_conversation.html', {'error': 'You cannot start a conversation with yourself.'})

            conversation, created = Conversation.objects.get_or_create(
                id=1  # Use any default id you prefer or remove this line if relying on Django's default behavior
            )

            if created:
                conversation.participants.add(request.user)

            conversation.participants.add(other_user)
            return redirect('chat_view', conversation_id=conversation.id)
        except User.DoesNotExist:
            return render(request, 'chat/create_conversation.html', {'error': 'User not found.'})

    return render(request, 'chat/create_conversation.html')


