from django.views import View
from django.http import HttpResponse, JsonResponse
from AI.tasks import run_emotion, run_comment
from AI.models import AI
from AI.tasks import run_pixray
from diary.models import Diary
from users.models import User
import json


class mainView(View):
    def post(self, request):
        data = json.loads(request.body)
        id = data['userId']
        data = AI.objects.select_related('diaryId').values_list(
            'diaryId', 'emotion', 'diaryId__date').filter(diaryId__userId=id)
        print(data)
        res = []
        for i in range(len(data)):
            temp = {
                "diaryId": data[i][0],
                "emotion": data[i][1],
                "date": data[i][2]
            }
            res.append(temp)

        jsonObj = json.dumps(res, default=str)
        sdata = json.loads(jsonObj)
        return JsonResponse(sdata, status=200, safe=False)

    def get(self, request):
        dId = request.GET['diaryId']
        dataD = Diary.objects.get(diaryId=dId)
        dataAI = AI.objects.get(diaryId=dId)
        sdata = {
            "diaryId": dataD.diaryId,
            "date": dataD.date,
            "weather": dataD.weather,
            "title": dataD.title,
            "contents": dataD.contents,
            "liked": dataD.liked,
            "image": dataAI.image,
            "comment": dataAI.comment,
            "emotion": dataAI.emotion
        }
        return JsonResponse(sdata, status=200)
    
    def put(self, request):
        return JsonResponse()


class writeView(View):
    def post(self, request):
        temp = json.loads(request.body)
        uId = temp['userId']
        Diary.objects.create(userId=User.objects.get(
            userId=uId), contents=temp['contents'], weather=temp['weather'], title=temp['title'])
        dId = Diary.objects.filter(userId=uId).last()
        doc = temp['contents']
        
        emotion = run_emotion.delay(doc, dId.diaryId)

        sdata = {
            "diaryId": dId.diaryId,
            "emotion": emotion.get(),
        }

        # js
        return JsonResponse(sdata, json_dumps_params={'ensure_ascii': False}, status=201)


class moodView(View):
    def post(self, request):
        data = json.loads(request.body)
        dId = data['diaryId']
        semo = data['emotion']
        uId = data['userId']
        aiModel = AI.objects.get(diaryId=dId)
        aiModel.emotion = semo

        doc = Diary.objects.get(diaryId=dId).contents
        userModel = User.objects.get(userId=uId)

        emotion = aiModel.emotion
        imageYN = userModel.imageYN
        commentYN = userModel.commentYN

        sdata = {
            "emotion": emotion,
        }

        if(imageYN == 1):
            comment = run_comment.delay(doc, dId.diaryId)
            sdata['comment'] = comment.get()
            aiModel.comment = sdata['comment']

        if(commentYN == 1):
            keyW, path = run_pixray.delay(doc, dId.diaryId)
            sdata['image'] = path.get()
            aiModel.image = sdata['image']
            print(keyW, path)

        aiModel.save()
        
        print(sdata['emotion'], sdata['comment'], sdata['image'])
        
        return JsonResponse(sdata, json_dumps_params={'ensure_ascii': False}, status=201)


class likeView(View):  # 즐겨찾기 페이지
    def get(self, request):
        id = request.GET['userId']
        data = AI.objects.select_related('diaryId').values_list(
            'diaryId', 'emotion', 'comment', 'diaryId__date', 'diaryId__weather', 'diaryId__title').filter(diaryId__userId=id, diaryId__liked=1)
        res = []
        for i in range(len(data)):
            temp = {
                "diaryId": data[i][0],
                "emotion": data[i][1],
                "comment": data[i][2],
                "date": data[i][3],
                "weather": data[i][4],
                "title": data[i][5],
            }
            res.append(temp)

        jsonObj = json.dumps(res, default=str)
        sdata = json.loads(jsonObj)
        return JsonResponse(sdata, status=200, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        dId = data['diaryId']
        dlike = data['liked']
        adata = Diary.objects.get(diaryId=dId)
        adata.liked = dlike
        adata.save()
        return JsonResponse({"message": "update success"}, status=201)
