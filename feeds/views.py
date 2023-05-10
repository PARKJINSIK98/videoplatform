from rest_framework.views import APIView
from feeds.models import Feed, Comment
from feeds.serializers import FeedListSerializer, FeedCreateSerializer, FeedDetailSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from hitcount.views import HitCountDetailView
from django.views.generic import ListView


class FeedListView(APIView, ListView):
    # 게시글마다 각각의 조회수가 필요할 것 같아 추가해뒀습니다
    model = Feed    
    count_hit = True 
    paginate_by = 12

    def get(self, request):
        feeds = Feed.objects.all().order_by("-created_at")
        seriailizer = FeedListSerializer(feeds, many=True)
        return Response(seriailizer.data, status=status.HTTP_200_OK)


class CommentsView(APIView):
    def get(self, request):
        # 댓글 가져오기
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # 댓글 생성
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

    def put(self, request, comment_id):
        # 댓글 수정
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "댓글이 없습니다."}, status=404)

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def delete(self, request, comment_id):
        # 댓글 삭제
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "댓글이 없습니다."}, status=404)
        comment.delete()
        return Response({"message": "삭제되었습니다."}, status=204)


class CommentsLikeView(APIView):
    # 좋아요
    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "댓글이 없습니다."}, status=404)

        comment.like_count += 1
        comment.save()
        return Response(status=204)


class CommentsDislikeView(APIView):
    # 싫어요
    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "댓글이 없습니다."}, status=404)

        comment.dislike_count += 1
        comment.save()





class FeedDetailView(APIView, HitCountDetailView):
    #feed 상세페이지

    # 조회수
    model = Feed    
    count_hit = True 
    
    # 탬플릿에서 조회수 나타내기
    # {# the total hits for the object #}
    # {{ hitcount.total_hits }}

    def get(self, request, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        serializer = FeedDetailSerializer(feed)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedCreateView(APIView):
    # feed 만들기 기능. 
    def post(self, request):
        serializer = FeedCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FeedLikeView(APIView):
    def post(self, request, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        if request.user in feed.likes.all():
            feed.likes.remove(request.user) # like 요청 유저가 없으면 제거
            return Response("좋아요", status=status.HTTP_200_OK)
        else:
            feed.likes.add(request.user) #like 요청 유저가 없으면 추가
            return Response("좋아요 취소!", status=status.HTTP_200_OK)
