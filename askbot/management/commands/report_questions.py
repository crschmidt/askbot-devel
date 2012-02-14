from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from optparse import make_option
from askbot import models

base_report_dir = "/ala-windfeedback1/qa/web/reports/tag"

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--full',
            action = 'store_true',
            dest = 'show_details',
            default = False,
            help = 'Show details for each question.'
        ),
        make_option('--file',
            action = 'store_true',
            dest = 'save_file',
            default = False,
            help = 'Save results to file.'
        ),
    )
    help = 'Print report about questions labeled with any of the provided tags'

    def handle(self, *args, **kwargs):
      tag_list =  models.Tag.objects.all().filter(deleted=False)
      for tag in tag_list:
        print tag
        tot_ans = 0
        tot_comm = 0
        tot_up = 0
        tot_dn = 0
        tot_no_ans = 0

        questions = models.Question.objects.filter(tags = tag).distinct()
        question_content_type = ContentType.objects.get_for_model(models.Question)
        answer_content_type = ContentType.objects.get_for_model(models.Answer)
        summary_str = 'Report: %s - %d Items\n\n' % (tag, len(questions))

        detail_str = ''
        data = {
                'id': 'ID',
                'title': 'Title',
                'upvotes': 'Up Votes',
                'downvotes': 'Down Votes',
                'answers': 'Answers',
                'comments': 'Comments'
            }
        summary_str += '%(id)6s %(title)-52s %(upvotes)7s %(downvotes)9s %(answers)7s %(comments)8s\n' % data
        for question in questions:
            question_votes = models.Vote.objects.filter(
                                        object_id = question.id,
                                        content_type = question_content_type
                                    )
            downvote_count = question_votes.filter(vote = models.Vote.VOTE_DOWN).count()
            upvote_count = question_votes.filter(vote = models.Vote.VOTE_UP).count()
            tot_dn += downvote_count
            tot_up += upvote_count
            tot_ans += question.answer_count
            tot_comm += question.comments.all().count()
            if question.answer_count == 0:
              tot_no_ans += 1

            data = {
                'id': question.id, 
                'title': question.title[:50],
                'full_title': question.title,
                'upvotes': upvote_count,
                'downvotes': downvote_count,
                'answers': question.answer_count,
                'comments': question.comments.all().count()
            }
            summary_str += '%(id)6s %(title)-52s %(upvotes)7d %(downvotes)9d %(answers)7d %(comments)8s\n' % data
            detail_str += 60*"=" + '\n'
            detail_str += '%(id)s - %(full_title)s - upvotes: %(upvotes)3d, downvotes: %(downvotes)3d\n\n' % data
            detail_str += question.text + '\n'
            if True:
                for comment in question.comments.all():
                    detail_str += 'Comment by %s\n' % comment.user.username
                    detail_str += comment.comment + '\n'
                for answer in question.answers.all():
                    detail_str += '------------------\n'
                    answer_votes = models.Vote.objects.filter(
                                                    content_type = answer_content_type,
                                                    object_id = answer.id
                                                )
                    data = {
                        'author': answer.author,
                        'downvotes': answer_votes.filter(vote = models.Vote.VOTE_DOWN).count(),
                        'upvotes': answer_votes.filter(vote = models.Vote.VOTE_UP).count(),
                    }
                    detail_str +=  'Answer by %(author)s - upvotes %(upvotes)d downvotes %(downvotes)d\n' % data
                    detail_str += answer.text + '\n'
                    for comment in answer.comments.all():
                        detail_str += 'Comment by %s\n' % comment.user.username
                        detail_str += comment.comment + '\n'
        data = {
                'title':'',
                'upvotes': '-------',
                'downvotes': '---------',
                'answers': '-------',
                'comments': '--------'
            }
        summary_str += '%(title)-59s %(upvotes)7s %(downvotes)9s %(answers)7s %(comments)8s\n' % data
        data = {
                'title':'  Total Items: %d - # Unanswered: %d' % (len(questions), tot_no_ans),
                'upvotes': tot_up,
                'downvotes': tot_dn,
                'answers': tot_ans,
                'comments':tot_comm 
            }
        summary_str += '%(title)-59s %(upvotes)7s %(downvotes)9s %(answers)7s %(comments)8s\n' % data
        if kwargs['save_file'] == True:
           fd = open("%s/%s.txt" % (base_report_dir , tag), 'w')
           fd.write(summary_str.encode("iso-8859-15", "replace"))
           if kwargs['show_details'] == True:
               fd.write(detail_str.encode("iso-8859-15","replace"))
           fd.close()
        else:
           print summary_str
           if kwargs['show_details'] == True:
               print detail_str

