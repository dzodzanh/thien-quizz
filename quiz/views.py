from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Exam, Question, Choice

def dashboard(request):
    exams = Exam.objects.all().order_by('-created_at')
    return render(request, 'quiz/dashboard.html', {'exams': exams})

def add_exam(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if not title:
            messages.error(request, 'Vui lòng nhập tên đề thi.')
            return redirect('quiz:add_exam')
            
        exam = Exam.objects.create(title=title, description=description)
        
        # Parse questions and choices
        question_count = int(request.POST.get('question_count', 0))
        for i in range(1, question_count + 1):
            q_text = request.POST.get(f'question_{i}_text')
            if q_text:
                question = Question.objects.create(exam=exam, text=q_text, order=i)
                
                # Choices for this question
                correct_choice = request.POST.get(f'question_{i}_correct') # e.g., '1', '2', '3', '4'
                
                for j in range(1, 5):
                    c_text = request.POST.get(f'question_{i}_choice_{j}')
                    if c_text:
                        is_correct = (str(j) == str(correct_choice))
                        Choice.objects.create(question=question, text=c_text, is_correct=is_correct)

        messages.success(request, 'Thêm đề bài thành công!')
        return redirect('quiz:dashboard')

    return render(request, 'quiz/add_exam.html')

def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()
    
    if request.method == 'POST':
        score = 0
        total = questions.count()
        
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                try:
                    choice = Choice.objects.get(id=selected_choice_id, question=question)
                    if choice.is_correct:
                        score += 1
                except Choice.DoesNotExist:
                    pass
                    
        return redirect('quiz:exam_result', exam_id=exam.id, score=score, total=total)
        
    return render(request, 'quiz/take_exam.html', {'exam': exam, 'questions': questions})

def exam_result(request, exam_id, score, total):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'quiz/result.html', {'exam': exam, 'score': score, 'total': total})

def delete_exam(request, exam_id):
    if request.method == 'POST':
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        messages.success(request, 'Xoá đề bài thành công.')
    return redirect('quiz:dashboard')
