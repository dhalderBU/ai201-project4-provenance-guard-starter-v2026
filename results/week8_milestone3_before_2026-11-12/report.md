# Five-criterion run — before

Produced by `run_eval.py::main`, `run_case`, and `summarize`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positive rate | At most 2/5 human pieces labelled AI | 0/5 AI | 0/5 AI | 0/5 AI | MET |
| 2. AI minus human mean score | Mean gap >= 0.30 (5 AI + 5 human) | 0.509418 | 0.509418 | 0.509418 | MET |
| 3. Correct labels | At least 4/5 correct labels | 4/5 | 4/5 | 4/5 | MET |
| 4. Appeal process | 5/5 appeals satisfy the recorded process | 5/5 | 5/5 | 5/5 | MET |
| 5. Complete and accurate audit entries | 10/10 requests logged in the required format | 6/10 | 6/10 | 6/10 | MISSED |

All raw requests, responses, checks, and trial metrics follow.

## 1. False positive rate

```json
{
  "criterion": 1,
  "name": "False positive rate",
  "target": "At most 2/5 human pieces labelled AI",
  "trials": [
    {
      "trial": 1,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "ai_labels": 0,
        "human_labels": 5,
        "unsure_labels": 0
      },
      "display": "0/5 AI",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c1_t1_own_1"
            },
            "sent_at_utc": "2026-11-12T10:54:59.785187+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_725ce0645369",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:03.810791+00:00",
            "duration_seconds": 4.025575042003766
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c1_t1_own_2"
            },
            "sent_at_utc": "2026-11-12T10:55:03.810969+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_eb54da8cd03e",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:03.918375+00:00",
            "duration_seconds": 0.10742641699471278
          }
        },
        {
          "id": "human_00000000_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "One reason is lots of catagories . However , how the NY Times calculates its best seller list is n't comprehensive , and is pretty well understood by publishers . So publishers can [ buy a few books ] ( URL_0 ) in the right bookstores and send a book to the top of the list for at least a week .",
              "creator_id": "eval_c1c9f55f_c1_t1_human_00000000_02"
            },
            "sent_at_utc": "2026-11-12T10:55:03.918792+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.22415613174594945,
              "confidence": 0.22415613174594945,
              "content_id": "c_bda3640abcf1",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2159,
              "style_score": 0.24342043915316483
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:03.995446+00:00",
            "duration_seconds": 0.07665829100005794
          }
        },
        {
          "id": "human_00000051_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Because we base most of those countries from what the Europeans called them . And some of those countries joined and devided and and they 're names changed over time . For example Germany was i think originally 3 tribes . One tribe called their land a word which we derived the name \" germany \" from . But another tribe called their land Deutschland . Guess which tribe eventually took all the land .",
              "creator_id": "eval_c1c9f55f_c1_t1_human_00000051_02"
            },
            "sent_at_utc": "2026-11-12T10:55:03.995761+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.31198281713367026,
              "confidence": 0.31198281713367026,
              "content_id": "c_07532df2f704",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2463,
              "style_score": 0.4652427237789009
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:04.073029+00:00",
            "duration_seconds": 0.0772667079945677
          }
        },
        {
          "id": "human_00000362_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "An exclamation point does n't imply yelling , it implies exclamation . You could exclaim something in a whisper , and it would be denoted with an exclamation point . The reason there is n't a mark for shouting or whispering is that English speaking societies simply have not felt it necessary to create marks specifically to indicate volume in speech .",
              "creator_id": "eval_c1c9f55f_c1_t1_human_00000362_02"
            },
            "sent_at_utc": "2026-11-12T10:55:04.073193+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.3227402060226801,
              "confidence": 0.3227402060226801,
              "content_id": "c_08daa2e36f03",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.3783,
              "style_score": 0.19310068674226705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:04.169142+00:00",
            "duration_seconds": 0.09595087500201771
          }
        }
      ]
    },
    {
      "trial": 2,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "ai_labels": 0,
        "human_labels": 5,
        "unsure_labels": 0
      },
      "display": "0/5 AI",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c1_t2_own_1"
            },
            "sent_at_utc": "2026-11-12T10:55:04.169357+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_414063c7ae54",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:04.266882+00:00",
            "duration_seconds": 0.09752545799710788
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c1_t2_own_2"
            },
            "sent_at_utc": "2026-11-12T10:55:04.267012+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_6e01fb142892",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:04.372849+00:00",
            "duration_seconds": 0.10583912499714643
          }
        },
        {
          "id": "human_00000000_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "One reason is lots of catagories . However , how the NY Times calculates its best seller list is n't comprehensive , and is pretty well understood by publishers . So publishers can [ buy a few books ] ( URL_0 ) in the right bookstores and send a book to the top of the list for at least a week .",
              "creator_id": "eval_c1c9f55f_c1_t2_human_00000000_02"
            },
            "sent_at_utc": "2026-11-12T10:55:04.373002+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.22415613174594945,
              "confidence": 0.22415613174594945,
              "content_id": "c_adf06833c4d2",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2159,
              "style_score": 0.24342043915316483
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:04.449035+00:00",
            "duration_seconds": 0.07603458299854537
          }
        },
        {
          "id": "human_00000051_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Because we base most of those countries from what the Europeans called them . And some of those countries joined and devided and and they 're names changed over time . For example Germany was i think originally 3 tribes . One tribe called their land a word which we derived the name \" germany \" from . But another tribe called their land Deutschland . Guess which tribe eventually took all the land .",
              "creator_id": "eval_c1c9f55f_c1_t2_human_00000051_02"
            },
            "sent_at_utc": "2026-11-12T10:55:04.449166+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.31198281713367026,
              "confidence": 0.31198281713367026,
              "content_id": "c_684ef0761834",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2463,
              "style_score": 0.4652427237789009
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:55:04.526142+00:00",
            "duration_seconds": 0.07698566599719925
          }
        },
        {
          "id": "human_00000362_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "An exclamation point does n't imply yelling , it implies exclamation . You could exclaim something in a whisper , and it would be denoted with an exclamation point . The reason there is n't a mark for shouting or whispering is that English speaking societies simply have not felt it necessary to create marks specifically to indicate volume in speech .",
              "creator_id": "eval_c1c9f55f_c1_t2_human_00000362_02"
            },
            "sent_at_utc": "2026-11-12T10:56:00.794688+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.3227402060226801,
              "confidence": 0.3227402060226801,
              "content_id": "c_22193bc25a36",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.3783,
              "style_score": 0.19310068674226705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:00.910123+00:00",
            "duration_seconds": 0.11542058299528435
          }
        }
      ]
    },
    {
      "trial": 3,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "ai_labels": 0,
        "human_labels": 5,
        "unsure_labels": 0
      },
      "display": "0/5 AI",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c1_t3_own_1"
            },
            "sent_at_utc": "2026-11-12T10:56:00.910723+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_9b7b3f0ac081",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.011944+00:00",
            "duration_seconds": 0.10123066700180061
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c1_t3_own_2"
            },
            "sent_at_utc": "2026-11-12T10:56:01.012512+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_df191bcc3d6e",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.119163+00:00",
            "duration_seconds": 0.10664449999603676
          }
        },
        {
          "id": "human_00000000_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "One reason is lots of catagories . However , how the NY Times calculates its best seller list is n't comprehensive , and is pretty well understood by publishers . So publishers can [ buy a few books ] ( URL_0 ) in the right bookstores and send a book to the top of the list for at least a week .",
              "creator_id": "eval_c1c9f55f_c1_t3_human_00000000_02"
            },
            "sent_at_utc": "2026-11-12T10:56:01.119279+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.22415613174594945,
              "confidence": 0.22415613174594945,
              "content_id": "c_1152ba69fff1",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2159,
              "style_score": 0.24342043915316483
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.197982+00:00",
            "duration_seconds": 0.07870425000146497
          }
        },
        {
          "id": "human_00000051_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Because we base most of those countries from what the Europeans called them . And some of those countries joined and devided and and they 're names changed over time . For example Germany was i think originally 3 tribes . One tribe called their land a word which we derived the name \" germany \" from . But another tribe called their land Deutschland . Guess which tribe eventually took all the land .",
              "creator_id": "eval_c1c9f55f_c1_t3_human_00000051_02"
            },
            "sent_at_utc": "2026-11-12T10:56:01.198107+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.31198281713367026,
              "confidence": 0.31198281713367026,
              "content_id": "c_a81a2427ca2c",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2463,
              "style_score": 0.4652427237789009
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.276950+00:00",
            "duration_seconds": 0.07884533299511531
          }
        },
        {
          "id": "human_00000362_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "An exclamation point does n't imply yelling , it implies exclamation . You could exclaim something in a whisper , and it would be denoted with an exclamation point . The reason there is n't a mark for shouting or whispering is that English speaking societies simply have not felt it necessary to create marks specifically to indicate volume in speech .",
              "creator_id": "eval_c1c9f55f_c1_t3_human_00000362_02"
            },
            "sent_at_utc": "2026-11-12T10:56:01.277127+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.3227402060226801,
              "confidence": 0.3227402060226801,
              "content_id": "c_e8405da3f088",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.3783,
              "style_score": 0.19310068674226705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.351989+00:00",
            "duration_seconds": 0.07490104200405767
          }
        }
      ]
    }
  ]
}
```

## 2. AI minus human mean score

```json
{
  "criterion": 2,
  "name": "AI minus human mean score",
  "target": "Mean gap >= 0.30 (5 AI + 5 human)",
  "trials": [
    {
      "trial": 1,
      "metrics": {
        "requests": 10,
        "all_submissions_scored": true,
        "human_mean": 0.27512793623016096,
        "ai_mean": 0.7845462862090351,
        "gap": 0.5094183499788741
      },
      "display": "0.509418",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c2_t1_own_1"
            },
            "sent_at_utc": "2026-11-12T10:56:01.352926+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_79128e5a5916",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.450618+00:00",
            "duration_seconds": 0.09769995799433673
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c2_t1_own_2"
            },
            "sent_at_utc": "2026-11-12T10:56:01.451120+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_d07f192b3b07",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.557760+00:00",
            "duration_seconds": 0.10665291699842783
          }
        },
        {
          "id": "human_00000000_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "One reason is lots of catagories . However , how the NY Times calculates its best seller list is n't comprehensive , and is pretty well understood by publishers . So publishers can [ buy a few books ] ( URL_0 ) in the right bookstores and send a book to the top of the list for at least a week .",
              "creator_id": "eval_c1c9f55f_c2_t1_human_00000000_02"
            },
            "sent_at_utc": "2026-11-12T10:56:01.558239+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.22415613174594945,
              "confidence": 0.22415613174594945,
              "content_id": "c_f3743511223c",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2159,
              "style_score": 0.24342043915316483
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:56:01.634030+00:00",
            "duration_seconds": 0.07580174999748124
          }
        },
        {
          "id": "human_00000051_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Because we base most of those countries from what the Europeans called them . And some of those countries joined and devided and and they 're names changed over time . For example Germany was i think originally 3 tribes . One tribe called their land a word which we derived the name \" germany \" from . But another tribe called their land Deutschland . Guess which tribe eventually took all the land .",
              "creator_id": "eval_c1c9f55f_c2_t1_human_00000051_02"
            },
            "sent_at_utc": "2026-11-12T10:57:01.805082+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.31198281713367026,
              "confidence": 0.31198281713367026,
              "content_id": "c_9e1ec8962a20",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2463,
              "style_score": 0.4652427237789009
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:01.925568+00:00",
            "duration_seconds": 0.12048274999688147
          }
        },
        {
          "id": "human_00000362_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "An exclamation point does n't imply yelling , it implies exclamation . You could exclaim something in a whisper , and it would be denoted with an exclamation point . The reason there is n't a mark for shouting or whispering is that English speaking societies simply have not felt it necessary to create marks specifically to indicate volume in speech .",
              "creator_id": "eval_c1c9f55f_c2_t1_human_00000362_02"
            },
            "sent_at_utc": "2026-11-12T10:57:01.926090+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.3227402060226801,
              "confidence": 0.3227402060226801,
              "content_id": "c_f10ce35c73f1",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.3783,
              "style_score": 0.19310068674226705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.005707+00:00",
            "duration_seconds": 0.07963179199578008
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c2_t1_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T10:57:02.006187+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_b9154818daa9",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.101780+00:00",
            "duration_seconds": 0.09560712500388036
          }
        },
        {
          "id": "ai_00000318_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Cars are often shaped aerodynamically to help them move more efficiently through the air. This can make them faster and use less fuel. Buses, on the other hand, are not usually designed to be as fast as cars and are not typically used for long distance travel. Buses are also generally larger and heavier than cars, so they may not benefit as much from an aerodynamic design. Additionally, buses often have other design considerations, such as the need to carry a large number of passengers and the need to be easily accessible to people with disabilities.",
              "creator_id": "eval_c1c9f55f_c2_t1_ai_00000318_00"
            },
            "sent_at_utc": "2026-11-12T10:57:02.102357+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.744801541251441,
              "confidence": 0.744801541251441,
              "content_id": "c_6137ccd7c37f",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9096,
              "style_score": 0.3602718041714705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.197773+00:00",
            "duration_seconds": 0.09542787499958649
          }
        },
        {
          "id": "ai_00000552_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I'm sorry, but I'm not aware of any current plans for John Stewart to leave The Daily Show. John Stewart was the host of The Daily Show from 1999 to 2015, and he has not been involved with the show since then. It is possible that you may be thinking of a different John Stewart or a different news program.",
              "creator_id": "eval_c1c9f55f_c2_t1_ai_00000552_00"
            },
            "sent_at_utc": "2026-11-12T10:57:02.198200+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8295,
              "confidence": 0.8295,
              "content_id": "c_9d8292755720",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.885,
              "style_score": 0.7000000000000002
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.274167+00:00",
            "duration_seconds": 0.07596429099794477
          }
        },
        {
          "id": "ai_00001008_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I'm sorry, but I'm not able to view or access the gif that you mentioned. Without being able to see the gif, I'm unable to provide an explanation for the behavior of the fish that you described. It's possible that the fish in the gif are exhibiting a behavior known as shoaling, which is when fish swim together in a group for protection and social interaction. However, I cannot confirm this without being able to see the gif.",
              "creator_id": "eval_c1c9f55f_c2_t1_ai_00001008_00"
            },
            "sent_at_utc": "2026-11-12T10:57:02.274300+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7768837034099993,
              "confidence": 0.7768837034099993,
              "content_id": "c_00a81f79c9af",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8698,
              "style_score": 0.5600790113666648
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.357766+00:00",
            "duration_seconds": 0.0834768329950748
          }
        },
        {
          "id": "ai_00001495_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "It's possible that some people grow neckbeards because they think it makes them look more attractive or masculine. However, it's important to note that neckbeards, like all physical appearances, are a matter of personal preference and people's opinions on them can vary widely. Some people may find neckbeards attractive, while others may not. Ultimately, people make choices about their appearance for a variety of reasons, and it's not always easy to understand or predict what those reasons might be. It's important to remember to be respectful of other people's choices and not judge them based on their appearance.",
              "creator_id": "eval_c1c9f55f_c2_t1_ai_00001495_00"
            },
            "sent_at_utc": "2026-11-12T10:57:02.358098+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7792451498845487,
              "confidence": 0.7792451498845487,
              "content_id": "c_1ebf3e3d335b",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9241,
              "style_score": 0.4412504996151629
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.459482+00:00",
            "duration_seconds": 0.10140595800476149
          }
        }
      ]
    },
    {
      "trial": 2,
      "metrics": {
        "requests": 10,
        "all_submissions_scored": true,
        "human_mean": 0.27512793623016096,
        "ai_mean": 0.7845462862090351,
        "gap": 0.5094183499788741
      },
      "display": "0.509418",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c2_t2_own_1"
            },
            "sent_at_utc": "2026-11-12T10:57:02.460200+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_770a4c85e185",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.560484+00:00",
            "duration_seconds": 0.10028645899728872
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c2_t2_own_2"
            },
            "sent_at_utc": "2026-11-12T10:57:02.560855+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_cbfecdeff367",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:57:02.665984+00:00",
            "duration_seconds": 0.10514174999843817
          }
        },
        {
          "id": "human_00000000_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "One reason is lots of catagories . However , how the NY Times calculates its best seller list is n't comprehensive , and is pretty well understood by publishers . So publishers can [ buy a few books ] ( URL_0 ) in the right bookstores and send a book to the top of the list for at least a week .",
              "creator_id": "eval_c1c9f55f_c2_t2_human_00000000_02"
            },
            "sent_at_utc": "2026-11-12T10:58:02.814916+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.22415613174594945,
              "confidence": 0.22415613174594945,
              "content_id": "c_b60e5cc50c39",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2159,
              "style_score": 0.24342043915316483
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:02.932910+00:00",
            "duration_seconds": 0.11798295900371158
          }
        },
        {
          "id": "human_00000051_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Because we base most of those countries from what the Europeans called them . And some of those countries joined and devided and and they 're names changed over time . For example Germany was i think originally 3 tribes . One tribe called their land a word which we derived the name \" germany \" from . But another tribe called their land Deutschland . Guess which tribe eventually took all the land .",
              "creator_id": "eval_c1c9f55f_c2_t2_human_00000051_02"
            },
            "sent_at_utc": "2026-11-12T10:58:02.933620+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.31198281713367026,
              "confidence": 0.31198281713367026,
              "content_id": "c_d2809008b9ab",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2463,
              "style_score": 0.4652427237789009
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.017922+00:00",
            "duration_seconds": 0.08430499999667518
          }
        },
        {
          "id": "human_00000362_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "An exclamation point does n't imply yelling , it implies exclamation . You could exclaim something in a whisper , and it would be denoted with an exclamation point . The reason there is n't a mark for shouting or whispering is that English speaking societies simply have not felt it necessary to create marks specifically to indicate volume in speech .",
              "creator_id": "eval_c1c9f55f_c2_t2_human_00000362_02"
            },
            "sent_at_utc": "2026-11-12T10:58:03.018372+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.3227402060226801,
              "confidence": 0.3227402060226801,
              "content_id": "c_7ccf68252d8b",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.3783,
              "style_score": 0.19310068674226705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.098689+00:00",
            "duration_seconds": 0.08032475000072736
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c2_t2_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T10:58:03.099129+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_a90c546e6d2f",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.199663+00:00",
            "duration_seconds": 0.10055004199966788
          }
        },
        {
          "id": "ai_00000318_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Cars are often shaped aerodynamically to help them move more efficiently through the air. This can make them faster and use less fuel. Buses, on the other hand, are not usually designed to be as fast as cars and are not typically used for long distance travel. Buses are also generally larger and heavier than cars, so they may not benefit as much from an aerodynamic design. Additionally, buses often have other design considerations, such as the need to carry a large number of passengers and the need to be easily accessible to people with disabilities.",
              "creator_id": "eval_c1c9f55f_c2_t2_ai_00000318_00"
            },
            "sent_at_utc": "2026-11-12T10:58:03.200255+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.744801541251441,
              "confidence": 0.744801541251441,
              "content_id": "c_9a41eba636f6",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9096,
              "style_score": 0.3602718041714705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.297596+00:00",
            "duration_seconds": 0.09734962500078836
          }
        },
        {
          "id": "ai_00000552_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I'm sorry, but I'm not aware of any current plans for John Stewart to leave The Daily Show. John Stewart was the host of The Daily Show from 1999 to 2015, and he has not been involved with the show since then. It is possible that you may be thinking of a different John Stewart or a different news program.",
              "creator_id": "eval_c1c9f55f_c2_t2_ai_00000552_00"
            },
            "sent_at_utc": "2026-11-12T10:58:03.298033+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8295,
              "confidence": 0.8295,
              "content_id": "c_e28b2ad052b1",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.885,
              "style_score": 0.7000000000000002
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.373757+00:00",
            "duration_seconds": 0.07573066699842457
          }
        },
        {
          "id": "ai_00001008_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I'm sorry, but I'm not able to view or access the gif that you mentioned. Without being able to see the gif, I'm unable to provide an explanation for the behavior of the fish that you described. It's possible that the fish in the gif are exhibiting a behavior known as shoaling, which is when fish swim together in a group for protection and social interaction. However, I cannot confirm this without being able to see the gif.",
              "creator_id": "eval_c1c9f55f_c2_t2_ai_00001008_00"
            },
            "sent_at_utc": "2026-11-12T10:58:03.374103+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7768837034099993,
              "confidence": 0.7768837034099993,
              "content_id": "c_d2d2b774a61a",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8698,
              "style_score": 0.5600790113666648
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.457266+00:00",
            "duration_seconds": 0.0831600410019746
          }
        },
        {
          "id": "ai_00001495_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "It's possible that some people grow neckbeards because they think it makes them look more attractive or masculine. However, it's important to note that neckbeards, like all physical appearances, are a matter of personal preference and people's opinions on them can vary widely. Some people may find neckbeards attractive, while others may not. Ultimately, people make choices about their appearance for a variety of reasons, and it's not always easy to understand or predict what those reasons might be. It's important to remember to be respectful of other people's choices and not judge them based on their appearance.",
              "creator_id": "eval_c1c9f55f_c2_t2_ai_00001495_00"
            },
            "sent_at_utc": "2026-11-12T10:58:03.457383+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7792451498845487,
              "confidence": 0.7792451498845487,
              "content_id": "c_295c613da3bd",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9241,
              "style_score": 0.4412504996151629
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.558199+00:00",
            "duration_seconds": 0.10082749999855878
          }
        }
      ]
    },
    {
      "trial": 3,
      "metrics": {
        "requests": 10,
        "all_submissions_scored": true,
        "human_mean": 0.27512793623016096,
        "ai_mean": 0.7845462862090351,
        "gap": 0.5094183499788741
      },
      "display": "0.509418",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c2_t3_own_1"
            },
            "sent_at_utc": "2026-11-12T10:58:03.558665+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_07331809aff4",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:58:03.657767+00:00",
            "duration_seconds": 0.09911791599733988
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c2_t3_own_2"
            },
            "sent_at_utc": "2026-11-12T10:59:03.823608+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_194b02e82b92",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:03.973532+00:00",
            "duration_seconds": 0.14990512499934994
          }
        },
        {
          "id": "human_00000000_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "One reason is lots of catagories . However , how the NY Times calculates its best seller list is n't comprehensive , and is pretty well understood by publishers . So publishers can [ buy a few books ] ( URL_0 ) in the right bookstores and send a book to the top of the list for at least a week .",
              "creator_id": "eval_c1c9f55f_c2_t3_human_00000000_02"
            },
            "sent_at_utc": "2026-11-12T10:59:03.974076+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.22415613174594945,
              "confidence": 0.22415613174594945,
              "content_id": "c_8a04140bd844",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2159,
              "style_score": 0.24342043915316483
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.055613+00:00",
            "duration_seconds": 0.08154883299721405
          }
        },
        {
          "id": "human_00000051_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Because we base most of those countries from what the Europeans called them . And some of those countries joined and devided and and they 're names changed over time . For example Germany was i think originally 3 tribes . One tribe called their land a word which we derived the name \" germany \" from . But another tribe called their land Deutschland . Guess which tribe eventually took all the land .",
              "creator_id": "eval_c1c9f55f_c2_t3_human_00000051_02"
            },
            "sent_at_utc": "2026-11-12T10:59:04.056161+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.31198281713367026,
              "confidence": 0.31198281713367026,
              "content_id": "c_16a102efc9c7",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2463,
              "style_score": 0.4652427237789009
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.137533+00:00",
            "duration_seconds": 0.08136749999539461
          }
        },
        {
          "id": "human_00000362_02",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "An exclamation point does n't imply yelling , it implies exclamation . You could exclaim something in a whisper , and it would be denoted with an exclamation point . The reason there is n't a mark for shouting or whispering is that English speaking societies simply have not felt it necessary to create marks specifically to indicate volume in speech .",
              "creator_id": "eval_c1c9f55f_c2_t3_human_00000362_02"
            },
            "sent_at_utc": "2026-11-12T10:59:04.137664+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.3227402060226801,
              "confidence": 0.3227402060226801,
              "content_id": "c_a8b4a3f030fd",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.3783,
              "style_score": 0.19310068674226705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.216076+00:00",
            "duration_seconds": 0.07841266700415872
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c2_t3_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T10:59:04.216185+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_fce82814e913",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.313661+00:00",
            "duration_seconds": 0.09748724999371916
          }
        },
        {
          "id": "ai_00000318_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Cars are often shaped aerodynamically to help them move more efficiently through the air. This can make them faster and use less fuel. Buses, on the other hand, are not usually designed to be as fast as cars and are not typically used for long distance travel. Buses are also generally larger and heavier than cars, so they may not benefit as much from an aerodynamic design. Additionally, buses often have other design considerations, such as the need to carry a large number of passengers and the need to be easily accessible to people with disabilities.",
              "creator_id": "eval_c1c9f55f_c2_t3_ai_00000318_00"
            },
            "sent_at_utc": "2026-11-12T10:59:04.314086+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.744801541251441,
              "confidence": 0.744801541251441,
              "content_id": "c_4a8bc32d3dc6",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9096,
              "style_score": 0.3602718041714705
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.411146+00:00",
            "duration_seconds": 0.09706849999929545
          }
        },
        {
          "id": "ai_00000552_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I'm sorry, but I'm not aware of any current plans for John Stewart to leave The Daily Show. John Stewart was the host of The Daily Show from 1999 to 2015, and he has not been involved with the show since then. It is possible that you may be thinking of a different John Stewart or a different news program.",
              "creator_id": "eval_c1c9f55f_c2_t3_ai_00000552_00"
            },
            "sent_at_utc": "2026-11-12T10:59:04.411500+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8295,
              "confidence": 0.8295,
              "content_id": "c_a70685539787",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.885,
              "style_score": 0.7000000000000002
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.488706+00:00",
            "duration_seconds": 0.07721858399600023
          }
        },
        {
          "id": "ai_00001008_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I'm sorry, but I'm not able to view or access the gif that you mentioned. Without being able to see the gif, I'm unable to provide an explanation for the behavior of the fish that you described. It's possible that the fish in the gif are exhibiting a behavior known as shoaling, which is when fish swim together in a group for protection and social interaction. However, I cannot confirm this without being able to see the gif.",
              "creator_id": "eval_c1c9f55f_c2_t3_ai_00001008_00"
            },
            "sent_at_utc": "2026-11-12T10:59:04.489075+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7768837034099993,
              "confidence": 0.7768837034099993,
              "content_id": "c_bae485f117cb",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8698,
              "style_score": 0.5600790113666648
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.572853+00:00",
            "duration_seconds": 0.08377729100175202
          }
        },
        {
          "id": "ai_00001495_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "It's possible that some people grow neckbeards because they think it makes them look more attractive or masculine. However, it's important to note that neckbeards, like all physical appearances, are a matter of personal preference and people's opinions on them can vary widely. Some people may find neckbeards attractive, while others may not. Ultimately, people make choices about their appearance for a variety of reasons, and it's not always easy to understand or predict what those reasons might be. It's important to remember to be respectful of other people's choices and not judge them based on their appearance.",
              "creator_id": "eval_c1c9f55f_c2_t3_ai_00001495_00"
            },
            "sent_at_utc": "2026-11-12T10:59:04.573001+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7792451498845487,
              "confidence": 0.7792451498845487,
              "content_id": "c_ebb2638be55e",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9241,
              "style_score": 0.4412504996151629
            },
            "error": null,
            "received_at_utc": "2026-11-12T10:59:04.674989+00:00",
            "duration_seconds": 0.10200737499690149
          }
        }
      ]
    }
  ]
}
```

## 3. Correct labels

```json
{
  "criterion": 3,
  "name": "Correct labels",
  "target": "At least 4/5 correct labels",
  "trials": [
    {
      "trial": 1,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "correct": 4,
        "labels_reached": [
          "ai",
          "human",
          "unsure"
        ],
        "expected_label_matches": 5,
        "criterion_band_matches": 4
      },
      "display": "4/5",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c3_t1_own_1"
            },
            "sent_at_utc": "2026-11-12T11:00:04.834004+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_94d8cf5542b6",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:04.975126+00:00",
            "duration_seconds": 0.1411080839970964
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_1",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. \nThere are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or magnesium chloride, or using mechanical methods like plows or sand. However, salt is often the most effective and affordable option for many communities, especially when it's used in combination with other methods. \nIt's important to note that while salt can be helpful for making roads safer during the winter, it can also have negative effects on the environment and on the cars themselves. Salt can cause corrosion on metal surfaces, including cars, and it can also harm plants and animals if it washes into nearby waterways. However, despite these potential downsides, many communities continue to use salt as a way to keep roads clear and safe during the winter.",
              "creator_id": "eval_c1c9f55f_c3_t1_coverage_1"
            },
            "sent_at_utc": "2026-11-12T11:00:04.975663+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8043489877961235,
              "confidence": 0.8043489877961235,
              "content_id": "c_b83436783658",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9134,
              "style_score": 0.5498966259870786
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:05.147078+00:00",
            "duration_seconds": 0.1714182920040912
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "They are one of the most compelling reasons to manage the livestock and food industry . Forget that they are nearly impossible to eliminate by cooking if they are in your foodstuffs . Forget the horrible , horrible way they kill . The only reason prions prolifferate is by feeding animal waste products back to your stock animals . Bovine spongiform , scrapie and CJD are all caused by eating an animals brain / spinal fluid . Surely this should not be happening ? People should have the right to trust their foodstuffs and should not be feeding dead animals back to other livestocks . That is what scares me .",
              "creator_id": "eval_c1c9f55f_c3_t1_coverage_2"
            },
            "sent_at_utc": "2026-11-12T11:00:05.147333+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.23462207011916347,
              "confidence": 0.23462207011916347,
              "content_id": "c_6d35d162247f",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2172,
              "style_score": 0.2752735670638783
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:05.258611+00:00",
            "duration_seconds": 0.11129641700244974
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_3",
          "authorship": "unsure",
          "expected_label": "unsure",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "`What's Love Got to Do With It' tells the harrowing story of Tina Turner's life and music, and her relationship with Ike Turner. The movie shows the violence and abuse she faced, and her struggles to break free to find success on her own.Tina found the strength to stand up to Ike. In a powerful scene towards the end of the movie  Ike slips past security into Tina's dressing room with a gun and Tina finds the inner strength to face him . The movie s  Angela Bassett as Tina and Laurence Fishburne as Ike, It  features the soundtrack of Tina Turners songs performed by Bassett and the movie also has a lot of great music in it too snd its a story of pain and courage, portraying Tina Turner's resilience and showcasing her incredible talent.",
              "creator_id": "eval_c1c9f55f_c3_t1_coverage_3"
            },
            "sent_at_utc": "2026-11-12T11:00:05.259106+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.4067944288261874,
              "confidence": 0.4067944288261874,
              "content_id": "c_62bc4d38ad46",
              "guess": "unsure",
              "label": "unsure",
              "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.",
              "model_score": 0.3474,
              "style_score": 0.5453814294206247
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:05.395926+00:00",
            "duration_seconds": 0.1368293750056182
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": false
          }
        },
        {
          "id": "demo_ai",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "The importance of effective time management cannot be overstated in today's fast-paced work environment. Professionals who develop strong organizational habits are better positioned to meet deadlines and reduce stress. There are several key strategies that can help individuals improve their productivity. First, prioritization is essential. By identifying the most important tasks and addressing them first, workers can ensure that critical objectives are met. Second, minimizing distractions plays a significant role. Setting aside dedicated blocks of time for concentrated work is widely considered beneficial. Finally, regular breaks are important for maintaining performance.",
              "creator_id": "eval_c1c9f55f_c3_t1_demo_ai"
            },
            "sent_at_utc": "2026-11-12T11:00:05.396416+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.6196043276276597,
              "confidence": 0.6196043276276597,
              "content_id": "c_870ab0c88566",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.7544,
              "style_score": 0.3050810920921994
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:05.493864+00:00",
            "duration_seconds": 0.09745579200534848
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        }
      ]
    },
    {
      "trial": 2,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "correct": 4,
        "labels_reached": [
          "ai",
          "human",
          "unsure"
        ],
        "expected_label_matches": 5,
        "criterion_band_matches": 4
      },
      "display": "4/5",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c3_t2_own_1"
            },
            "sent_at_utc": "2026-11-12T11:00:05.494418+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_444b4436d846",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:05.596481+00:00",
            "duration_seconds": 0.10207470799650764
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_1",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. \nThere are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or magnesium chloride, or using mechanical methods like plows or sand. However, salt is often the most effective and affordable option for many communities, especially when it's used in combination with other methods. \nIt's important to note that while salt can be helpful for making roads safer during the winter, it can also have negative effects on the environment and on the cars themselves. Salt can cause corrosion on metal surfaces, including cars, and it can also harm plants and animals if it washes into nearby waterways. However, despite these potential downsides, many communities continue to use salt as a way to keep roads clear and safe during the winter.",
              "creator_id": "eval_c1c9f55f_c3_t2_coverage_1"
            },
            "sent_at_utc": "2026-11-12T11:00:05.596953+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8043489877961235,
              "confidence": 0.8043489877961235,
              "content_id": "c_ac3c8de68c48",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9134,
              "style_score": 0.5498966259870786
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:05.765003+00:00",
            "duration_seconds": 0.16806416700273985
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "They are one of the most compelling reasons to manage the livestock and food industry . Forget that they are nearly impossible to eliminate by cooking if they are in your foodstuffs . Forget the horrible , horrible way they kill . The only reason prions prolifferate is by feeding animal waste products back to your stock animals . Bovine spongiform , scrapie and CJD are all caused by eating an animals brain / spinal fluid . Surely this should not be happening ? People should have the right to trust their foodstuffs and should not be feeding dead animals back to other livestocks . That is what scares me .",
              "creator_id": "eval_c1c9f55f_c3_t2_coverage_2"
            },
            "sent_at_utc": "2026-11-12T11:00:05.765514+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.23462207011916347,
              "confidence": 0.23462207011916347,
              "content_id": "c_5dc0f5e03628",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2172,
              "style_score": 0.2752735670638783
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:05.873848+00:00",
            "duration_seconds": 0.10834637500374811
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_3",
          "authorship": "unsure",
          "expected_label": "unsure",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "`What's Love Got to Do With It' tells the harrowing story of Tina Turner's life and music, and her relationship with Ike Turner. The movie shows the violence and abuse she faced, and her struggles to break free to find success on her own.Tina found the strength to stand up to Ike. In a powerful scene towards the end of the movie  Ike slips past security into Tina's dressing room with a gun and Tina finds the inner strength to face him . The movie s  Angela Bassett as Tina and Laurence Fishburne as Ike, It  features the soundtrack of Tina Turners songs performed by Bassett and the movie also has a lot of great music in it too snd its a story of pain and courage, portraying Tina Turner's resilience and showcasing her incredible talent.",
              "creator_id": "eval_c1c9f55f_c3_t2_coverage_3"
            },
            "sent_at_utc": "2026-11-12T11:00:05.874434+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.4067944288261874,
              "confidence": 0.4067944288261874,
              "content_id": "c_4bde40601ca5",
              "guess": "unsure",
              "label": "unsure",
              "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.",
              "model_score": 0.3474,
              "style_score": 0.5453814294206247
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:00:06.008436+00:00",
            "duration_seconds": 0.13400849999743514
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": false
          }
        },
        {
          "id": "demo_ai",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "The importance of effective time management cannot be overstated in today's fast-paced work environment. Professionals who develop strong organizational habits are better positioned to meet deadlines and reduce stress. There are several key strategies that can help individuals improve their productivity. First, prioritization is essential. By identifying the most important tasks and addressing them first, workers can ensure that critical objectives are met. Second, minimizing distractions plays a significant role. Setting aside dedicated blocks of time for concentrated work is widely considered beneficial. Finally, regular breaks are important for maintaining performance.",
              "creator_id": "eval_c1c9f55f_c3_t2_demo_ai"
            },
            "sent_at_utc": "2026-11-12T11:01:05.834445+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.6196043276276597,
              "confidence": 0.6196043276276597,
              "content_id": "c_5bfeddcbf94c",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.7544,
              "style_score": 0.3050810920921994
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:05.975660+00:00",
            "duration_seconds": 0.14118833300017286
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        }
      ]
    },
    {
      "trial": 3,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "correct": 4,
        "labels_reached": [
          "ai",
          "human",
          "unsure"
        ],
        "expected_label_matches": 5,
        "criterion_band_matches": 4
      },
      "display": "4/5",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c3_t3_own_1"
            },
            "sent_at_utc": "2026-11-12T11:01:05.976224+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_f3208df25296",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.080178+00:00",
            "duration_seconds": 0.1039675840002019
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_1",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. \nThere are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or magnesium chloride, or using mechanical methods like plows or sand. However, salt is often the most effective and affordable option for many communities, especially when it's used in combination with other methods. \nIt's important to note that while salt can be helpful for making roads safer during the winter, it can also have negative effects on the environment and on the cars themselves. Salt can cause corrosion on metal surfaces, including cars, and it can also harm plants and animals if it washes into nearby waterways. However, despite these potential downsides, many communities continue to use salt as a way to keep roads clear and safe during the winter.",
              "creator_id": "eval_c1c9f55f_c3_t3_coverage_1"
            },
            "sent_at_utc": "2026-11-12T11:01:06.080692+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8043489877961235,
              "confidence": 0.8043489877961235,
              "content_id": "c_adad224529be",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9134,
              "style_score": 0.5498966259870786
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.246129+00:00",
            "duration_seconds": 0.1654505829937989
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "They are one of the most compelling reasons to manage the livestock and food industry . Forget that they are nearly impossible to eliminate by cooking if they are in your foodstuffs . Forget the horrible , horrible way they kill . The only reason prions prolifferate is by feeding animal waste products back to your stock animals . Bovine spongiform , scrapie and CJD are all caused by eating an animals brain / spinal fluid . Surely this should not be happening ? People should have the right to trust their foodstuffs and should not be feeding dead animals back to other livestocks . That is what scares me .",
              "creator_id": "eval_c1c9f55f_c3_t3_coverage_2"
            },
            "sent_at_utc": "2026-11-12T11:01:06.246630+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.23462207011916347,
              "confidence": 0.23462207011916347,
              "content_id": "c_152bc3c02850",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.2172,
              "style_score": 0.2752735670638783
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.355671+00:00",
            "duration_seconds": 0.10904416699486319
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        },
        {
          "id": "coverage_3",
          "authorship": "unsure",
          "expected_label": "unsure",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "`What's Love Got to Do With It' tells the harrowing story of Tina Turner's life and music, and her relationship with Ike Turner. The movie shows the violence and abuse she faced, and her struggles to break free to find success on her own.Tina found the strength to stand up to Ike. In a powerful scene towards the end of the movie  Ike slips past security into Tina's dressing room with a gun and Tina finds the inner strength to face him . The movie s  Angela Bassett as Tina and Laurence Fishburne as Ike, It  features the soundtrack of Tina Turners songs performed by Bassett and the movie also has a lot of great music in it too snd its a story of pain and courage, portraying Tina Turner's resilience and showcasing her incredible talent.",
              "creator_id": "eval_c1c9f55f_c3_t3_coverage_3"
            },
            "sent_at_utc": "2026-11-12T11:01:06.355971+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.4067944288261874,
              "confidence": 0.4067944288261874,
              "content_id": "c_55635c611fd8",
              "guess": "unsure",
              "label": "unsure",
              "label_text": "We do not have enough evidence to determine how this text was written. The writer can request a review.",
              "model_score": 0.3474,
              "style_score": 0.5453814294206247
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.489440+00:00",
            "duration_seconds": 0.13348545799817657
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": false
          }
        },
        {
          "id": "demo_ai",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "The importance of effective time management cannot be overstated in today's fast-paced work environment. Professionals who develop strong organizational habits are better positioned to meet deadlines and reduce stress. There are several key strategies that can help individuals improve their productivity. First, prioritization is essential. By identifying the most important tasks and addressing them first, workers can ensure that critical objectives are met. Second, minimizing distractions plays a significant role. Setting aside dedicated blocks of time for concentrated work is widely considered beneficial. Finally, regular breaks are important for maintaining performance.",
              "creator_id": "eval_c1c9f55f_c3_t3_demo_ai"
            },
            "sent_at_utc": "2026-11-12T11:01:06.489954+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.6196043276276597,
              "confidence": 0.6196043276276597,
              "content_id": "c_4a544420309f",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.7544,
              "style_score": 0.3050810920921994
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.588383+00:00",
            "duration_seconds": 0.09844445799535606
          },
          "checks": {
            "scored": true,
            "expected_label": true,
            "criterion_band": true
          }
        }
      ]
    }
  ]
}
```

## 4. Appeal process

```json
{
  "criterion": 4,
  "name": "Appeal process",
  "target": "5/5 appeals satisfy the recorded process",
  "trials": [
    {
      "trial": 1,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "passed": 5,
        "failures": []
      },
      "display": "5/5",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c4_t1_own_1"
            },
            "sent_at_utc": "2026-11-12T11:01:06.592708+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_229d2aa94117",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.693723+00:00",
            "duration_seconds": 0.1010050830009277
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_229d2aa94117",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:01:06.693735+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_e5765a91403a",
              "content_id": "c_229d2aa94117",
              "evaluations": [
                {
                  "combined_score": 0.3466417865508413,
                  "label": "human",
                  "model_score": 0.1592,
                  "status": "scored",
                  "style_score": 0.6278044663771033,
                  "variant": "original"
                },
                {
                  "combined_score": 0.3318261224489795,
                  "label": "human",
                  "model_score": 0.1442,
                  "status": "scored",
                  "style_score": 0.6132653061224488,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3438275362489148,
                  "label": "human",
                  "model_score": 0.165,
                  "status": "scored",
                  "style_score": 0.612068840622287,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 0,
                "human": 3,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.795018+00:00",
            "duration_seconds": 0.10128491599607514
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_229d2aa94117",
            "request": null,
            "sent_at_utc": "2026-11-12T11:01:06.795026+00:00",
            "status": 200,
            "response": {
              "content_id": "c_229d2aa94117",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.797682+00:00",
            "duration_seconds": 0.0026594579976517707
          },
          "audit_entries": [
            {
              "appeal_id": "a_e5765a91403a",
              "content_id": "c_229d2aa94117",
              "creator_id": "eval_c1c9f55f_c4_t1_own_1",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:01:06+00:00"
            },
            {
              "appeal_id": "a_e5765a91403a",
              "content_id": "c_229d2aa94117",
              "creator_id": "eval_c1c9f55f_c4_t1_own_1",
              "evaluations": [
                {
                  "combined_score": 0.3466417865508413,
                  "label": "human",
                  "model_score": 0.1592,
                  "status": "scored",
                  "style_score": 0.6278044663771033,
                  "variant": "original"
                },
                {
                  "combined_score": 0.3318261224489795,
                  "label": "human",
                  "model_score": 0.1442,
                  "status": "scored",
                  "style_score": 0.6132653061224488,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3438275362489148,
                  "label": "human",
                  "model_score": 0.165,
                  "status": "scored",
                  "style_score": 0.612068840622287,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:01:06+00:00",
              "votes": {
                "ai": 0,
                "human": 3,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c4_t1_own_2"
            },
            "sent_at_utc": "2026-11-12T11:01:06.803885+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_dad4141d045e",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:06.909756+00:00",
            "duration_seconds": 0.10588666699914029
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_dad4141d045e",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:01:06.909803+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_4ca05ecde1d2",
              "content_id": "c_dad4141d045e",
              "evaluations": [
                {
                  "combined_score": 0.3837989151138318,
                  "label": "human",
                  "model_score": 0.281,
                  "status": "scored",
                  "style_score": 0.5379972877845794,
                  "variant": "original"
                },
                {
                  "combined_score": 0.4047642289225172,
                  "label": "unsure",
                  "model_score": 0.3209,
                  "status": "scored",
                  "style_score": 0.5305605723062929,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3963098113207548,
                  "label": "human",
                  "model_score": 0.2819,
                  "status": "scored",
                  "style_score": 0.567924528301887,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 0,
                "human": 2,
                "unsure": 1
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:07.019094+00:00",
            "duration_seconds": 0.10930679099692497
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_dad4141d045e",
            "request": null,
            "sent_at_utc": "2026-11-12T11:01:07.019136+00:00",
            "status": 200,
            "response": {
              "content_id": "c_dad4141d045e",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:07.023159+00:00",
            "duration_seconds": 0.004026417002023663
          },
          "audit_entries": [
            {
              "appeal_id": "a_4ca05ecde1d2",
              "content_id": "c_dad4141d045e",
              "creator_id": "eval_c1c9f55f_c4_t1_own_2",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:01:06+00:00"
            },
            {
              "appeal_id": "a_4ca05ecde1d2",
              "content_id": "c_dad4141d045e",
              "creator_id": "eval_c1c9f55f_c4_t1_own_2",
              "evaluations": [
                {
                  "combined_score": 0.3837989151138318,
                  "label": "human",
                  "model_score": 0.281,
                  "status": "scored",
                  "style_score": 0.5379972877845794,
                  "variant": "original"
                },
                {
                  "combined_score": 0.4047642289225172,
                  "label": "unsure",
                  "model_score": 0.3209,
                  "status": "scored",
                  "style_score": 0.5305605723062929,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3963098113207548,
                  "label": "human",
                  "model_score": 0.2819,
                  "status": "scored",
                  "style_score": 0.567924528301887,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:01:07+00:00",
              "votes": {
                "ai": 0,
                "human": 2,
                "unsure": 1
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c4_t1_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T11:01:07.032006+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_686fc7b2557f",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:07.130281+00:00",
            "duration_seconds": 0.09827320800104644
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_686fc7b2557f",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:01:07.130293+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_3c005797e5a1",
              "content_id": "c_686fc7b2557f",
              "evaluations": [
                {
                  "combined_score": 0.7613347153322488,
                  "label": "ai",
                  "model_score": 0.8852,
                  "status": "scored",
                  "style_score": 0.5755367883306223,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7417178802577131,
                  "label": "ai",
                  "model_score": 0.8585,
                  "status": "scored",
                  "style_score": 0.5665447006442826,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7419168405460653,
                  "label": "ai",
                  "model_score": 0.8527,
                  "status": "scored",
                  "style_score": 0.5757421013651634,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:07.226524+00:00",
            "duration_seconds": 0.09623295799974585
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_686fc7b2557f",
            "request": null,
            "sent_at_utc": "2026-11-12T11:01:07.226533+00:00",
            "status": 200,
            "response": {
              "content_id": "c_686fc7b2557f",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:01:07.275752+00:00",
            "duration_seconds": 0.049242959001276176
          },
          "audit_entries": [
            {
              "appeal_id": "a_3c005797e5a1",
              "content_id": "c_686fc7b2557f",
              "creator_id": "eval_c1c9f55f_c4_t1_ai_00000113_00",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:01:07+00:00"
            },
            {
              "appeal_id": "a_3c005797e5a1",
              "content_id": "c_686fc7b2557f",
              "creator_id": "eval_c1c9f55f_c4_t1_ai_00000113_00",
              "evaluations": [
                {
                  "combined_score": 0.7613347153322488,
                  "label": "ai",
                  "model_score": 0.8852,
                  "status": "scored",
                  "style_score": 0.5755367883306223,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7417178802577131,
                  "label": "ai",
                  "model_score": 0.8585,
                  "status": "scored",
                  "style_score": 0.5665447006442826,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7419168405460653,
                  "label": "ai",
                  "model_score": 0.8527,
                  "status": "scored",
                  "style_score": 0.5757421013651634,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:01:07+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "ai_00001495_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "It's possible that some people grow neckbeards because they think it makes them look more attractive or masculine. However, it's important to note that neckbeards, like all physical appearances, are a matter of personal preference and people's opinions on them can vary widely. Some people may find neckbeards attractive, while others may not. Ultimately, people make choices about their appearance for a variety of reasons, and it's not always easy to understand or predict what those reasons might be. It's important to remember to be respectful of other people's choices and not judge them based on their appearance.",
              "creator_id": "eval_c1c9f55f_c4_t1_ai_00001495_00"
            },
            "sent_at_utc": "2026-11-12T11:02:06.836336+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7792451498845487,
              "confidence": 0.7792451498845487,
              "content_id": "c_39b6a6993598",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9241,
              "style_score": 0.4412504996151629
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:06.985878+00:00",
            "duration_seconds": 0.1495357499952661
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_39b6a6993598",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:06.985928+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_0414f74ca9fb",
              "content_id": "c_39b6a6993598",
              "evaluations": [
                {
                  "combined_score": 0.7309601998460651,
                  "label": "ai",
                  "model_score": 0.9241,
                  "status": "scored",
                  "style_score": 0.4412504996151629,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7257496848377449,
                  "label": "ai",
                  "model_score": 0.9162,
                  "status": "scored",
                  "style_score": 0.4400742120943623,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7212811912767676,
                  "label": "ai",
                  "model_score": 0.9136,
                  "status": "scored",
                  "style_score": 0.43280297819191915,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.099575+00:00",
            "duration_seconds": 0.11365808300615754
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_39b6a6993598",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:07.099607+00:00",
            "status": 200,
            "response": {
              "content_id": "c_39b6a6993598",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.103655+00:00",
            "duration_seconds": 0.0040492920015822165
          },
          "audit_entries": [
            {
              "appeal_id": "a_0414f74ca9fb",
              "content_id": "c_39b6a6993598",
              "creator_id": "eval_c1c9f55f_c4_t1_ai_00001495_00",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:06+00:00"
            },
            {
              "appeal_id": "a_0414f74ca9fb",
              "content_id": "c_39b6a6993598",
              "creator_id": "eval_c1c9f55f_c4_t1_ai_00001495_00",
              "evaluations": [
                {
                  "combined_score": 0.7309601998460651,
                  "label": "ai",
                  "model_score": 0.9241,
                  "status": "scored",
                  "style_score": 0.4412504996151629,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7257496848377449,
                  "label": "ai",
                  "model_score": 0.9162,
                  "status": "scored",
                  "style_score": 0.4400742120943623,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7212811912767676,
                  "label": "ai",
                  "model_score": 0.9136,
                  "status": "scored",
                  "style_score": 0.43280297819191915,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:07+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "coverage_1",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. \nThere are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or magnesium chloride, or using mechanical methods like plows or sand. However, salt is often the most effective and affordable option for many communities, especially when it's used in combination with other methods. \nIt's important to note that while salt can be helpful for making roads safer during the winter, it can also have negative effects on the environment and on the cars themselves. Salt can cause corrosion on metal surfaces, including cars, and it can also harm plants and animals if it washes into nearby waterways. However, despite these potential downsides, many communities continue to use salt as a way to keep roads clear and safe during the winter.",
              "creator_id": "eval_c1c9f55f_c4_t1_coverage_1"
            },
            "sent_at_utc": "2026-11-12T11:02:07.111405+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8043489877961235,
              "confidence": 0.8043489877961235,
              "content_id": "c_bc6bb69e1881",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9134,
              "style_score": 0.5498966259870786
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.274931+00:00",
            "duration_seconds": 0.1635413330004667
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_bc6bb69e1881",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:07.274971+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_b678497a9200",
              "content_id": "c_bc6bb69e1881",
              "evaluations": [
                {
                  "combined_score": 0.7502986503948315,
                  "label": "ai",
                  "model_score": 0.8839,
                  "status": "scored",
                  "style_score": 0.5498966259870786,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7499419789050726,
                  "label": "ai",
                  "model_score": 0.8788,
                  "status": "scored",
                  "style_score": 0.5566549472626817,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7351380427446571,
                  "label": "ai",
                  "model_score": 0.8658,
                  "status": "scored",
                  "style_score": 0.539145106861643,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.442182+00:00",
            "duration_seconds": 0.16721558300196193
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_bc6bb69e1881",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:07.442200+00:00",
            "status": 200,
            "response": {
              "content_id": "c_bc6bb69e1881",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.445534+00:00",
            "duration_seconds": 0.0033422499982407317
          },
          "audit_entries": [
            {
              "appeal_id": "a_b678497a9200",
              "content_id": "c_bc6bb69e1881",
              "creator_id": "eval_c1c9f55f_c4_t1_coverage_1",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:07+00:00"
            },
            {
              "appeal_id": "a_b678497a9200",
              "content_id": "c_bc6bb69e1881",
              "creator_id": "eval_c1c9f55f_c4_t1_coverage_1",
              "evaluations": [
                {
                  "combined_score": 0.7502986503948315,
                  "label": "ai",
                  "model_score": 0.8839,
                  "status": "scored",
                  "style_score": 0.5498966259870786,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7499419789050726,
                  "label": "ai",
                  "model_score": 0.8788,
                  "status": "scored",
                  "style_score": 0.5566549472626817,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7351380427446571,
                  "label": "ai",
                  "model_score": 0.8658,
                  "status": "scored",
                  "style_score": 0.539145106861643,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:07+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        }
      ]
    },
    {
      "trial": 2,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "passed": 5,
        "failures": []
      },
      "display": "5/5",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c4_t2_own_1"
            },
            "sent_at_utc": "2026-11-12T11:02:07.453792+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_492e5409fe37",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.558684+00:00",
            "duration_seconds": 0.10491191599430749
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_492e5409fe37",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:07.558732+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_bbd0548bfabb",
              "content_id": "c_492e5409fe37",
              "evaluations": [
                {
                  "combined_score": 0.3466417865508413,
                  "label": "human",
                  "model_score": 0.1592,
                  "status": "scored",
                  "style_score": 0.6278044663771033,
                  "variant": "original"
                },
                {
                  "combined_score": 0.3318261224489795,
                  "label": "human",
                  "model_score": 0.1442,
                  "status": "scored",
                  "style_score": 0.6132653061224488,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3438275362489148,
                  "label": "human",
                  "model_score": 0.165,
                  "status": "scored",
                  "style_score": 0.612068840622287,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 0,
                "human": 3,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.670004+00:00",
            "duration_seconds": 0.11128654100321
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_492e5409fe37",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:07.670044+00:00",
            "status": 200,
            "response": {
              "content_id": "c_492e5409fe37",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.674394+00:00",
            "duration_seconds": 0.004358707999926992
          },
          "audit_entries": [
            {
              "appeal_id": "a_bbd0548bfabb",
              "content_id": "c_492e5409fe37",
              "creator_id": "eval_c1c9f55f_c4_t2_own_1",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:07+00:00"
            },
            {
              "appeal_id": "a_bbd0548bfabb",
              "content_id": "c_492e5409fe37",
              "creator_id": "eval_c1c9f55f_c4_t2_own_1",
              "evaluations": [
                {
                  "combined_score": 0.3466417865508413,
                  "label": "human",
                  "model_score": 0.1592,
                  "status": "scored",
                  "style_score": 0.6278044663771033,
                  "variant": "original"
                },
                {
                  "combined_score": 0.3318261224489795,
                  "label": "human",
                  "model_score": 0.1442,
                  "status": "scored",
                  "style_score": 0.6132653061224488,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3438275362489148,
                  "label": "human",
                  "model_score": 0.165,
                  "status": "scored",
                  "style_score": 0.612068840622287,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:07+00:00",
              "votes": {
                "ai": 0,
                "human": 3,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c4_t2_own_2"
            },
            "sent_at_utc": "2026-11-12T11:02:07.685006+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_5ee2a803dcf4",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.796440+00:00",
            "duration_seconds": 0.11145141699671512
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_5ee2a803dcf4",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:07.796487+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_5472e7896fbf",
              "content_id": "c_5ee2a803dcf4",
              "evaluations": [
                {
                  "combined_score": 0.3837989151138318,
                  "label": "human",
                  "model_score": 0.281,
                  "status": "scored",
                  "style_score": 0.5379972877845794,
                  "variant": "original"
                },
                {
                  "combined_score": 0.4047642289225172,
                  "label": "unsure",
                  "model_score": 0.3209,
                  "status": "scored",
                  "style_score": 0.5305605723062929,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3963098113207548,
                  "label": "human",
                  "model_score": 0.2819,
                  "status": "scored",
                  "style_score": 0.567924528301887,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 0,
                "human": 2,
                "unsure": 1
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.910247+00:00",
            "duration_seconds": 0.11377741699834587
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_5ee2a803dcf4",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:07.910290+00:00",
            "status": 200,
            "response": {
              "content_id": "c_5ee2a803dcf4",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:07.914586+00:00",
            "duration_seconds": 0.004304082998714875
          },
          "audit_entries": [
            {
              "appeal_id": "a_5472e7896fbf",
              "content_id": "c_5ee2a803dcf4",
              "creator_id": "eval_c1c9f55f_c4_t2_own_2",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:07+00:00"
            },
            {
              "appeal_id": "a_5472e7896fbf",
              "content_id": "c_5ee2a803dcf4",
              "creator_id": "eval_c1c9f55f_c4_t2_own_2",
              "evaluations": [
                {
                  "combined_score": 0.3837989151138318,
                  "label": "human",
                  "model_score": 0.281,
                  "status": "scored",
                  "style_score": 0.5379972877845794,
                  "variant": "original"
                },
                {
                  "combined_score": 0.4047642289225172,
                  "label": "unsure",
                  "model_score": 0.3209,
                  "status": "scored",
                  "style_score": 0.5305605723062929,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3963098113207548,
                  "label": "human",
                  "model_score": 0.2819,
                  "status": "scored",
                  "style_score": 0.567924528301887,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:07+00:00",
              "votes": {
                "ai": 0,
                "human": 2,
                "unsure": 1
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c4_t2_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T11:02:07.924602+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_798b3b251049",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.024485+00:00",
            "duration_seconds": 0.0999033749976661
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_798b3b251049",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:08.024537+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_0dea9ccc8dd8",
              "content_id": "c_798b3b251049",
              "evaluations": [
                {
                  "combined_score": 0.7613347153322488,
                  "label": "ai",
                  "model_score": 0.8852,
                  "status": "scored",
                  "style_score": 0.5755367883306223,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7417178802577131,
                  "label": "ai",
                  "model_score": 0.8585,
                  "status": "scored",
                  "style_score": 0.5665447006442826,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7419168405460653,
                  "label": "ai",
                  "model_score": 0.8527,
                  "status": "scored",
                  "style_score": 0.5757421013651634,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.133421+00:00",
            "duration_seconds": 0.10888149999664165
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_798b3b251049",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:08.133431+00:00",
            "status": 200,
            "response": {
              "content_id": "c_798b3b251049",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.136048+00:00",
            "duration_seconds": 0.0026193750018137507
          },
          "audit_entries": [
            {
              "appeal_id": "a_0dea9ccc8dd8",
              "content_id": "c_798b3b251049",
              "creator_id": "eval_c1c9f55f_c4_t2_ai_00000113_00",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00"
            },
            {
              "appeal_id": "a_0dea9ccc8dd8",
              "content_id": "c_798b3b251049",
              "creator_id": "eval_c1c9f55f_c4_t2_ai_00000113_00",
              "evaluations": [
                {
                  "combined_score": 0.7613347153322488,
                  "label": "ai",
                  "model_score": 0.8852,
                  "status": "scored",
                  "style_score": 0.5755367883306223,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7417178802577131,
                  "label": "ai",
                  "model_score": 0.8585,
                  "status": "scored",
                  "style_score": 0.5665447006442826,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7419168405460653,
                  "label": "ai",
                  "model_score": 0.8527,
                  "status": "scored",
                  "style_score": 0.5757421013651634,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "ai_00001495_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "It's possible that some people grow neckbeards because they think it makes them look more attractive or masculine. However, it's important to note that neckbeards, like all physical appearances, are a matter of personal preference and people's opinions on them can vary widely. Some people may find neckbeards attractive, while others may not. Ultimately, people make choices about their appearance for a variety of reasons, and it's not always easy to understand or predict what those reasons might be. It's important to remember to be respectful of other people's choices and not judge them based on their appearance.",
              "creator_id": "eval_c1c9f55f_c4_t2_ai_00001495_00"
            },
            "sent_at_utc": "2026-11-12T11:02:08.142449+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7792451498845487,
              "confidence": 0.7792451498845487,
              "content_id": "c_c93e4e3ef276",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9241,
              "style_score": 0.4412504996151629
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.266039+00:00",
            "duration_seconds": 0.12359137500607176
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_c93e4e3ef276",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:08.266051+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_03dcd97b85c1",
              "content_id": "c_c93e4e3ef276",
              "evaluations": [
                {
                  "combined_score": 0.7309601998460651,
                  "label": "ai",
                  "model_score": 0.9241,
                  "status": "scored",
                  "style_score": 0.4412504996151629,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7257496848377449,
                  "label": "ai",
                  "model_score": 0.9162,
                  "status": "scored",
                  "style_score": 0.4400742120943623,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7212811912767676,
                  "label": "ai",
                  "model_score": 0.9136,
                  "status": "scored",
                  "style_score": 0.43280297819191915,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.379039+00:00",
            "duration_seconds": 0.1129902500033495
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_c93e4e3ef276",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:08.379048+00:00",
            "status": 200,
            "response": {
              "content_id": "c_c93e4e3ef276",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.381634+00:00",
            "duration_seconds": 0.002587041999504436
          },
          "audit_entries": [
            {
              "appeal_id": "a_03dcd97b85c1",
              "content_id": "c_c93e4e3ef276",
              "creator_id": "eval_c1c9f55f_c4_t2_ai_00001495_00",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00"
            },
            {
              "appeal_id": "a_03dcd97b85c1",
              "content_id": "c_c93e4e3ef276",
              "creator_id": "eval_c1c9f55f_c4_t2_ai_00001495_00",
              "evaluations": [
                {
                  "combined_score": 0.7309601998460651,
                  "label": "ai",
                  "model_score": 0.9241,
                  "status": "scored",
                  "style_score": 0.4412504996151629,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7257496848377449,
                  "label": "ai",
                  "model_score": 0.9162,
                  "status": "scored",
                  "style_score": 0.4400742120943623,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7212811912767676,
                  "label": "ai",
                  "model_score": 0.9136,
                  "status": "scored",
                  "style_score": 0.43280297819191915,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "coverage_1",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. \nThere are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or magnesium chloride, or using mechanical methods like plows or sand. However, salt is often the most effective and affordable option for many communities, especially when it's used in combination with other methods. \nIt's important to note that while salt can be helpful for making roads safer during the winter, it can also have negative effects on the environment and on the cars themselves. Salt can cause corrosion on metal surfaces, including cars, and it can also harm plants and animals if it washes into nearby waterways. However, despite these potential downsides, many communities continue to use salt as a way to keep roads clear and safe during the winter.",
              "creator_id": "eval_c1c9f55f_c4_t2_coverage_1"
            },
            "sent_at_utc": "2026-11-12T11:02:08.387930+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8043489877961235,
              "confidence": 0.8043489877961235,
              "content_id": "c_83656752b1b5",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9134,
              "style_score": 0.5498966259870786
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.554179+00:00",
            "duration_seconds": 0.16626208299567224
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_83656752b1b5",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:08.554218+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_13e35d37f1f8",
              "content_id": "c_83656752b1b5",
              "evaluations": [
                {
                  "combined_score": 0.7502986503948315,
                  "label": "ai",
                  "model_score": 0.8839,
                  "status": "scored",
                  "style_score": 0.5498966259870786,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7499419789050726,
                  "label": "ai",
                  "model_score": 0.8788,
                  "status": "scored",
                  "style_score": 0.5566549472626817,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7351380427446571,
                  "label": "ai",
                  "model_score": 0.8658,
                  "status": "scored",
                  "style_score": 0.539145106861643,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.723580+00:00",
            "duration_seconds": 0.1693592079973314
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_83656752b1b5",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:08.723588+00:00",
            "status": 200,
            "response": {
              "content_id": "c_83656752b1b5",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.726286+00:00",
            "duration_seconds": 0.0027060840002377518
          },
          "audit_entries": [
            {
              "appeal_id": "a_13e35d37f1f8",
              "content_id": "c_83656752b1b5",
              "creator_id": "eval_c1c9f55f_c4_t2_coverage_1",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00"
            },
            {
              "appeal_id": "a_13e35d37f1f8",
              "content_id": "c_83656752b1b5",
              "creator_id": "eval_c1c9f55f_c4_t2_coverage_1",
              "evaluations": [
                {
                  "combined_score": 0.7502986503948315,
                  "label": "ai",
                  "model_score": 0.8839,
                  "status": "scored",
                  "style_score": 0.5498966259870786,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7499419789050726,
                  "label": "ai",
                  "model_score": 0.8788,
                  "status": "scored",
                  "style_score": 0.5566549472626817,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7351380427446571,
                  "label": "ai",
                  "model_score": 0.8658,
                  "status": "scored",
                  "style_score": 0.539145106861643,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        }
      ]
    },
    {
      "trial": 3,
      "metrics": {
        "requests": 5,
        "all_submissions_scored": true,
        "passed": 5,
        "failures": []
      },
      "display": "5/5",
      "verdict": "MET",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c4_t3_own_1"
            },
            "sent_at_utc": "2026-11-12T11:02:08.734917+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_008584828b02",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.838683+00:00",
            "duration_seconds": 0.10377633300231537
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_008584828b02",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:08.838724+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_f3a66efd6833",
              "content_id": "c_008584828b02",
              "evaluations": [
                {
                  "combined_score": 0.3466417865508413,
                  "label": "human",
                  "model_score": 0.1592,
                  "status": "scored",
                  "style_score": 0.6278044663771033,
                  "variant": "original"
                },
                {
                  "combined_score": 0.3318261224489795,
                  "label": "human",
                  "model_score": 0.1442,
                  "status": "scored",
                  "style_score": 0.6132653061224488,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3438275362489148,
                  "label": "human",
                  "model_score": 0.165,
                  "status": "scored",
                  "style_score": 0.612068840622287,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 0,
                "human": 3,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.947329+00:00",
            "duration_seconds": 0.10861633300373796
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_008584828b02",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:08.947366+00:00",
            "status": 200,
            "response": {
              "content_id": "c_008584828b02",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:08.951581+00:00",
            "duration_seconds": 0.004219875001581386
          },
          "audit_entries": [
            {
              "appeal_id": "a_f3a66efd6833",
              "content_id": "c_008584828b02",
              "creator_id": "eval_c1c9f55f_c4_t3_own_1",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00"
            },
            {
              "appeal_id": "a_f3a66efd6833",
              "content_id": "c_008584828b02",
              "creator_id": "eval_c1c9f55f_c4_t3_own_1",
              "evaluations": [
                {
                  "combined_score": 0.3466417865508413,
                  "label": "human",
                  "model_score": 0.1592,
                  "status": "scored",
                  "style_score": 0.6278044663771033,
                  "variant": "original"
                },
                {
                  "combined_score": 0.3318261224489795,
                  "label": "human",
                  "model_score": 0.1442,
                  "status": "scored",
                  "style_score": 0.6132653061224488,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3438275362489148,
                  "label": "human",
                  "model_score": 0.165,
                  "status": "scored",
                  "style_score": 0.612068840622287,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:08+00:00",
              "votes": {
                "ai": 0,
                "human": 3,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "own_2",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
              "creator_id": "eval_c1c9f55f_c4_t3_own_2"
            },
            "sent_at_utc": "2026-11-12T11:02:08.962037+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.26870918633537383,
              "confidence": 0.26870918633537383,
              "content_id": "c_cfeef25e5125",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.1533,
              "style_score": 0.5379972877845794
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:09.073195+00:00",
            "duration_seconds": 0.11117037499934668
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_cfeef25e5125",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:02:09.073235+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_d9846b169113",
              "content_id": "c_cfeef25e5125",
              "evaluations": [
                {
                  "combined_score": 0.3837989151138318,
                  "label": "human",
                  "model_score": 0.281,
                  "status": "scored",
                  "style_score": 0.5379972877845794,
                  "variant": "original"
                },
                {
                  "combined_score": 0.4047642289225172,
                  "label": "unsure",
                  "model_score": 0.3209,
                  "status": "scored",
                  "style_score": 0.5305605723062929,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3963098113207548,
                  "label": "human",
                  "model_score": 0.2819,
                  "status": "scored",
                  "style_score": 0.567924528301887,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 0,
                "human": 2,
                "unsure": 1
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:09.189485+00:00",
            "duration_seconds": 0.11624683300033212
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_cfeef25e5125",
            "request": null,
            "sent_at_utc": "2026-11-12T11:02:09.189494+00:00",
            "status": 200,
            "response": {
              "content_id": "c_cfeef25e5125",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:02:09.192113+00:00",
            "duration_seconds": 0.0026211249933112413
          },
          "audit_entries": [
            {
              "appeal_id": "a_d9846b169113",
              "content_id": "c_cfeef25e5125",
              "creator_id": "eval_c1c9f55f_c4_t3_own_2",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:09+00:00"
            },
            {
              "appeal_id": "a_d9846b169113",
              "content_id": "c_cfeef25e5125",
              "creator_id": "eval_c1c9f55f_c4_t3_own_2",
              "evaluations": [
                {
                  "combined_score": 0.3837989151138318,
                  "label": "human",
                  "model_score": 0.281,
                  "status": "scored",
                  "style_score": 0.5379972877845794,
                  "variant": "original"
                },
                {
                  "combined_score": 0.4047642289225172,
                  "label": "unsure",
                  "model_score": 0.3209,
                  "status": "scored",
                  "style_score": 0.5305605723062929,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.3963098113207548,
                  "label": "human",
                  "model_score": 0.2819,
                  "status": "scored",
                  "style_score": 0.567924528301887,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "message": "Your appeal has been recorded. Your submission is marked for review.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:02:09+00:00",
              "votes": {
                "ai": 0,
                "human": 2,
                "unsure": 1
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c4_t3_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T11:03:07.846734+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_217279253b33",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:07.994339+00:00",
            "duration_seconds": 0.14757900000404334
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_217279253b33",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:03:07.994364+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_a2597fd63a4d",
              "content_id": "c_217279253b33",
              "evaluations": [
                {
                  "combined_score": 0.7613347153322488,
                  "label": "ai",
                  "model_score": 0.8852,
                  "status": "scored",
                  "style_score": 0.5755367883306223,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7417178802577131,
                  "label": "ai",
                  "model_score": 0.8585,
                  "status": "scored",
                  "style_score": 0.5665447006442826,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7419168405460653,
                  "label": "ai",
                  "model_score": 0.8527,
                  "status": "scored",
                  "style_score": 0.5757421013651634,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.097754+00:00",
            "duration_seconds": 0.10340625000389991
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_217279253b33",
            "request": null,
            "sent_at_utc": "2026-11-12T11:03:08.097793+00:00",
            "status": 200,
            "response": {
              "content_id": "c_217279253b33",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.102026+00:00",
            "duration_seconds": 0.004240041998855304
          },
          "audit_entries": [
            {
              "appeal_id": "a_a2597fd63a4d",
              "content_id": "c_217279253b33",
              "creator_id": "eval_c1c9f55f_c4_t3_ai_00000113_00",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:03:07+00:00"
            },
            {
              "appeal_id": "a_a2597fd63a4d",
              "content_id": "c_217279253b33",
              "creator_id": "eval_c1c9f55f_c4_t3_ai_00000113_00",
              "evaluations": [
                {
                  "combined_score": 0.7613347153322488,
                  "label": "ai",
                  "model_score": 0.8852,
                  "status": "scored",
                  "style_score": 0.5755367883306223,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7417178802577131,
                  "label": "ai",
                  "model_score": 0.8585,
                  "status": "scored",
                  "style_score": 0.5665447006442826,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7419168405460653,
                  "label": "ai",
                  "model_score": 0.8527,
                  "status": "scored",
                  "style_score": 0.5757421013651634,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:03:08+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "ai_00001495_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "It's possible that some people grow neckbeards because they think it makes them look more attractive or masculine. However, it's important to note that neckbeards, like all physical appearances, are a matter of personal preference and people's opinions on them can vary widely. Some people may find neckbeards attractive, while others may not. Ultimately, people make choices about their appearance for a variety of reasons, and it's not always easy to understand or predict what those reasons might be. It's important to remember to be respectful of other people's choices and not judge them based on their appearance.",
              "creator_id": "eval_c1c9f55f_c4_t3_ai_00001495_00"
            },
            "sent_at_utc": "2026-11-12T11:03:08.112181+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7792451498845487,
              "confidence": 0.7792451498845487,
              "content_id": "c_2519b2a48318",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9241,
              "style_score": 0.4412504996151629
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.220191+00:00",
            "duration_seconds": 0.10802333299943712
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_2519b2a48318",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:03:08.220235+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_35c5e1f4fd67",
              "content_id": "c_2519b2a48318",
              "evaluations": [
                {
                  "combined_score": 0.7309601998460651,
                  "label": "ai",
                  "model_score": 0.9241,
                  "status": "scored",
                  "style_score": 0.4412504996151629,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7257496848377449,
                  "label": "ai",
                  "model_score": 0.9162,
                  "status": "scored",
                  "style_score": 0.4400742120943623,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7212811912767676,
                  "label": "ai",
                  "model_score": 0.9136,
                  "status": "scored",
                  "style_score": 0.43280297819191915,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.333672+00:00",
            "duration_seconds": 0.11345383300067624
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_2519b2a48318",
            "request": null,
            "sent_at_utc": "2026-11-12T11:03:08.333715+00:00",
            "status": 200,
            "response": {
              "content_id": "c_2519b2a48318",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.338149+00:00",
            "duration_seconds": 0.004443042002094444
          },
          "audit_entries": [
            {
              "appeal_id": "a_35c5e1f4fd67",
              "content_id": "c_2519b2a48318",
              "creator_id": "eval_c1c9f55f_c4_t3_ai_00001495_00",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:03:08+00:00"
            },
            {
              "appeal_id": "a_35c5e1f4fd67",
              "content_id": "c_2519b2a48318",
              "creator_id": "eval_c1c9f55f_c4_t3_ai_00001495_00",
              "evaluations": [
                {
                  "combined_score": 0.7309601998460651,
                  "label": "ai",
                  "model_score": 0.9241,
                  "status": "scored",
                  "style_score": 0.4412504996151629,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7257496848377449,
                  "label": "ai",
                  "model_score": 0.9162,
                  "status": "scored",
                  "style_score": 0.4400742120943623,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7212811912767676,
                  "label": "ai",
                  "model_score": 0.9136,
                  "status": "scored",
                  "style_score": 0.43280297819191915,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:03:08+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        },
        {
          "id": "coverage_1",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. \nThere are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or magnesium chloride, or using mechanical methods like plows or sand. However, salt is often the most effective and affordable option for many communities, especially when it's used in combination with other methods. \nIt's important to note that while salt can be helpful for making roads safer during the winter, it can also have negative effects on the environment and on the cars themselves. Salt can cause corrosion on metal surfaces, including cars, and it can also harm plants and animals if it washes into nearby waterways. However, despite these potential downsides, many communities continue to use salt as a way to keep roads clear and safe during the winter.",
              "creator_id": "eval_c1c9f55f_c4_t3_coverage_1"
            },
            "sent_at_utc": "2026-11-12T11:03:08.348784+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.8043489877961235,
              "confidence": 0.8043489877961235,
              "content_id": "c_c8bdf933e58b",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.9134,
              "style_score": 0.5498966259870786
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.516143+00:00",
            "duration_seconds": 0.16737837500113528
          },
          "appeal": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/appeal",
            "request": {
              "content_id": "c_c8bdf933e58b",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants."
            },
            "sent_at_utc": "2026-11-12T11:03:08.516209+00:00",
            "status": 200,
            "response": {
              "appeal_id": "a_46e223bca4e4",
              "content_id": "c_c8bdf933e58b",
              "evaluations": [
                {
                  "combined_score": 0.7502986503948315,
                  "label": "ai",
                  "model_score": 0.8839,
                  "status": "scored",
                  "style_score": 0.5498966259870786,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7499419789050726,
                  "label": "ai",
                  "model_score": 0.8788,
                  "status": "scored",
                  "style_score": 0.5566549472626817,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7351380427446571,
                  "label": "ai",
                  "model_score": 0.8658,
                  "status": "scored",
                  "style_score": 0.539145106861643,
                  "variant": "without_last_sentence"
                }
              ],
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.693086+00:00",
            "duration_seconds": 0.17687999999907333
          },
          "status_readback": {
            "method": "GET",
            "url": "http://127.0.0.1:5000/content/c_c8bdf933e58b",
            "request": null,
            "sent_at_utc": "2026-11-12T11:03:08.693108+00:00",
            "status": 200,
            "response": {
              "content_id": "c_c8bdf933e58b",
              "credential": null,
              "status": "under_review"
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.696633+00:00",
            "duration_seconds": 0.003532000002451241
          },
          "audit_entries": [
            {
              "appeal_id": "a_46e223bca4e4",
              "content_id": "c_c8bdf933e58b",
              "creator_id": "eval_c1c9f55f_c4_t3_coverage_1",
              "event": "appeal",
              "reasoning": "Please review this evaluation against the retained original and both sentence-removal variants.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:03:08+00:00"
            },
            {
              "appeal_id": "a_46e223bca4e4",
              "content_id": "c_c8bdf933e58b",
              "creator_id": "eval_c1c9f55f_c4_t3_coverage_1",
              "evaluations": [
                {
                  "combined_score": 0.7502986503948315,
                  "label": "ai",
                  "model_score": 0.8839,
                  "status": "scored",
                  "style_score": 0.5498966259870786,
                  "variant": "original"
                },
                {
                  "combined_score": 0.7499419789050726,
                  "label": "ai",
                  "model_score": 0.8788,
                  "status": "scored",
                  "style_score": 0.5566549472626817,
                  "variant": "without_first_sentence"
                },
                {
                  "combined_score": 0.7351380427446571,
                  "label": "ai",
                  "model_score": 0.8658,
                  "status": "scored",
                  "style_score": 0.539145106861643,
                  "variant": "without_last_sentence"
                }
              ],
              "event": "appeal_reassessment",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "message": "Your appeal has been recorded. Your submission is marked for review. Due to the nature of the mathematical computation involved in arriving at the conclusion, it is possible that the text has been evaluated as AI-written even though it was written by a human. If that is the case, please request human re-evaluation and submit earlier versions of the work so it can be evaluated by a person.",
              "review_type": "automatic",
              "status": "under_review",
              "timestamp": "2026-11-12T11:03:08+00:00",
              "votes": {
                "ai": 3,
                "human": 0,
                "unsure": 0
              },
              "weights": {
                "model": 0.6,
                "style": 0.4
              }
            }
          ],
          "checks": {
            "accepted": true,
            "under_review": true,
            "status_readback": true,
            "appeal_logged": true,
            "result_logged": true,
            "three_variants": true,
            "weights": true,
            "scored_with_60_40": true,
            "majority": true,
            "message": true
          }
        }
      ]
    }
  ]
}
```

## 5. Complete and accurate audit entries

```json
{
  "criterion": 5,
  "name": "Complete and accurate audit entries",
  "target": "10/10 requests logged in the required format",
  "trials": [
    {
      "trial": 1,
      "metrics": {
        "requests": 10,
        "all_submissions_scored": false,
        "passed": 6,
        "failures": [
          {
            "case": "null_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "empty_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "whitespace_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "object_creator",
            "failed_checks": [
              "creator_id"
            ]
          }
        ]
      },
      "display": "6/10",
      "verdict": "MISSED",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c5_t1_own_1"
            },
            "sent_at_utc": "2026-11-12T11:03:08.716838+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_e28f85f29f9c",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.825396+00:00",
            "duration_seconds": 0.10858054100390291
          },
          "audit_entries": [
            {
              "binoculars_score": 0.0113,
              "binoculars_used": true,
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_e28f85f29f9c",
              "creator_id": "eval_c1c9f55f_c5_t1_own_1",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "perplexity_score": 0.1592,
              "status": "decided",
              "style_score": 0.6278044663771033,
              "timestamp": "2026-11-12T11:03:08+00:00",
              "word_count": 101
            }
          ],
          "audit_count_before": 626,
          "audit_count_after": 627,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "required_fields": true,
            "response_matches": true,
            "confidence_matches_combined": true,
            "decided": true
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c5_t1_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T11:03:08.844565+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_4f10a62bf9e8",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.947411+00:00",
            "duration_seconds": 0.10286179100512527
          },
          "audit_entries": [
            {
              "binoculars_score": 0.9584,
              "binoculars_used": false,
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_4f10a62bf9e8",
              "creator_id": "eval_c1c9f55f_c5_t1_ai_00000113_00",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "perplexity_score": 0.8852,
              "status": "decided",
              "style_score": 0.5755367883306223,
              "timestamp": "2026-11-12T11:03:08+00:00",
              "word_count": 96
            }
          ],
          "audit_count_before": 627,
          "audit_count_after": 628,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "required_fields": true,
            "response_matches": true,
            "confidence_matches_combined": true,
            "decided": true
          }
        },
        {
          "id": "empty_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": "eval_c1c9f55f_c5_t1_empty_text"
            },
            "sent_at_utc": "2026-11-12T11:03:08.966312+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.968190+00:00",
            "duration_seconds": 0.0018808750028256327
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t1_empty_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:03:08+00:00"
            }
          ],
          "audit_count_before": 628,
          "audit_count_after": 629,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "missing_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "creator_id": "eval_c1c9f55f_c5_t1_missing_text"
            },
            "sent_at_utc": "2026-11-12T11:03:08.984486+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:08.986109+00:00",
            "duration_seconds": 0.0016242499987129122
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t1_missing_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:03:08+00:00"
            }
          ],
          "audit_count_before": 629,
          "audit_count_after": 630,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "list_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": [
                "not",
                "a",
                "string"
              ],
              "creator_id": "eval_c1c9f55f_c5_t1_list_text"
            },
            "sent_at_utc": "2026-11-12T11:03:09.001830+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:09.003594+00:00",
            "duration_seconds": 0.0017642500024521723
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t1_list_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:03:09+00:00"
            }
          ],
          "audit_count_before": 630,
          "audit_count_after": 631,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "null_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": null
            },
            "sent_at_utc": "2026-11-12T11:03:09.016171+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:03:09.017409+00:00",
            "duration_seconds": 0.0012395829980960116
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": null,
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:03:09+00:00"
            }
          ],
          "audit_count_before": 631,
          "audit_count_after": 632,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "empty_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": ""
            },
            "sent_at_utc": "2026-11-12T11:04:08.884861+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:08.888961+00:00",
            "duration_seconds": 0.004115249997994397
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:04:08+00:00"
            }
          ],
          "audit_count_before": 632,
          "audit_count_after": 633,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "whitespace_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": "   "
            },
            "sent_at_utc": "2026-11-12T11:04:08.928139+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:08.936664+00:00",
            "duration_seconds": 0.00853987500158837
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "   ",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:04:08+00:00"
            }
          ],
          "audit_count_before": 633,
          "audit_count_after": 634,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "object_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": {
                "name": "invalid"
              }
            },
            "sent_at_utc": "2026-11-12T11:04:08.965743+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:08.968712+00:00",
            "duration_seconds": 0.0029760000034002587
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": {
                "name": "invalid"
              },
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:04:08+00:00"
            }
          ],
          "audit_count_before": 634,
          "audit_count_after": 635,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "missing_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": ""
            },
            "sent_at_utc": "2026-11-12T11:04:08.989003+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:08.990711+00:00",
            "duration_seconds": 0.0017085840008803643
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "unknown",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:04:08+00:00"
            }
          ],
          "audit_count_before": 635,
          "audit_count_after": 636,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        }
      ]
    },
    {
      "trial": 2,
      "metrics": {
        "requests": 10,
        "all_submissions_scored": false,
        "passed": 6,
        "failures": [
          {
            "case": "null_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "empty_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "whitespace_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "object_creator",
            "failed_checks": [
              "creator_id"
            ]
          }
        ]
      },
      "display": "6/10",
      "verdict": "MISSED",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c5_t2_own_1"
            },
            "sent_at_utc": "2026-11-12T11:04:09.007351+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_01bc49599389",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:09.110942+00:00",
            "duration_seconds": 0.1036134999958449
          },
          "audit_entries": [
            {
              "binoculars_score": 0.0113,
              "binoculars_used": true,
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_01bc49599389",
              "creator_id": "eval_c1c9f55f_c5_t2_own_1",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "perplexity_score": 0.1592,
              "status": "decided",
              "style_score": 0.6278044663771033,
              "timestamp": "2026-11-12T11:04:09+00:00",
              "word_count": 101
            }
          ],
          "audit_count_before": 636,
          "audit_count_after": 637,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "required_fields": true,
            "response_matches": true,
            "confidence_matches_combined": true,
            "decided": true
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c5_t2_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T11:04:09.130949+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_ce0fea78ae8d",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:09.233410+00:00",
            "duration_seconds": 0.10247858300135704
          },
          "audit_entries": [
            {
              "binoculars_score": 0.9584,
              "binoculars_used": false,
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_ce0fea78ae8d",
              "creator_id": "eval_c1c9f55f_c5_t2_ai_00000113_00",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "perplexity_score": 0.8852,
              "status": "decided",
              "style_score": 0.5755367883306223,
              "timestamp": "2026-11-12T11:04:09+00:00",
              "word_count": 96
            }
          ],
          "audit_count_before": 637,
          "audit_count_after": 638,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "required_fields": true,
            "response_matches": true,
            "confidence_matches_combined": true,
            "decided": true
          }
        },
        {
          "id": "empty_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": "eval_c1c9f55f_c5_t2_empty_text"
            },
            "sent_at_utc": "2026-11-12T11:04:09.252641+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:09.254426+00:00",
            "duration_seconds": 0.0017866249982034788
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t2_empty_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:04:09+00:00"
            }
          ],
          "audit_count_before": 638,
          "audit_count_after": 639,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "missing_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "creator_id": "eval_c1c9f55f_c5_t2_missing_text"
            },
            "sent_at_utc": "2026-11-12T11:04:09.271263+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:09.273109+00:00",
            "duration_seconds": 0.0018518330034567043
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t2_missing_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:04:09+00:00"
            }
          ],
          "audit_count_before": 639,
          "audit_count_after": 640,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "list_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": [
                "not",
                "a",
                "string"
              ],
              "creator_id": "eval_c1c9f55f_c5_t2_list_text"
            },
            "sent_at_utc": "2026-11-12T11:04:09.287430+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:04:09.288753+00:00",
            "duration_seconds": 0.0013238750034361146
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t2_list_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:04:09+00:00"
            }
          ],
          "audit_count_before": 640,
          "audit_count_after": 641,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "null_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": null
            },
            "sent_at_utc": "2026-11-12T11:05:09.894147+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:09.898152+00:00",
            "duration_seconds": 0.0040110830013873056
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": null,
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:05:09+00:00"
            }
          ],
          "audit_count_before": 641,
          "audit_count_after": 642,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "empty_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": ""
            },
            "sent_at_utc": "2026-11-12T11:05:09.933531+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:09.936404+00:00",
            "duration_seconds": 0.0028743329967255704
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:05:09+00:00"
            }
          ],
          "audit_count_before": 642,
          "audit_count_after": 643,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "whitespace_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": "   "
            },
            "sent_at_utc": "2026-11-12T11:05:09.968226+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:09.971030+00:00",
            "duration_seconds": 0.0028109170016250573
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "   ",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:05:09+00:00"
            }
          ],
          "audit_count_before": 643,
          "audit_count_after": 644,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "object_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": {
                "name": "invalid"
              }
            },
            "sent_at_utc": "2026-11-12T11:05:10.000287+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:10.002595+00:00",
            "duration_seconds": 0.0023110839974833652
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": {
                "name": "invalid"
              },
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:05:10+00:00"
            }
          ],
          "audit_count_before": 644,
          "audit_count_after": 645,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "missing_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": ""
            },
            "sent_at_utc": "2026-11-12T11:05:10.028157+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:10.030580+00:00",
            "duration_seconds": 0.00242341699777171
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "unknown",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:05:10+00:00"
            }
          ],
          "audit_count_before": 645,
          "audit_count_after": 646,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        }
      ]
    },
    {
      "trial": 3,
      "metrics": {
        "requests": 10,
        "all_submissions_scored": false,
        "passed": 6,
        "failures": [
          {
            "case": "null_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "empty_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "whitespace_creator",
            "failed_checks": [
              "creator_id"
            ]
          },
          {
            "case": "object_creator",
            "failed_checks": [
              "creator_id"
            ]
          }
        ]
      },
      "display": "6/10",
      "verdict": "MISSED",
      "cases": [
        {
          "id": "own_1",
          "authorship": "human",
          "expected_label": "human",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
              "creator_id": "eval_c1c9f55f_c5_t3_own_1"
            },
            "sent_at_utc": "2026-11-12T11:05:10.051770+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_ea2e14f31109",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "style_score": 0.6278044663771033
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:10.163347+00:00",
            "duration_seconds": 0.1115892919988255
          },
          "audit_entries": [
            {
              "binoculars_score": 0.0113,
              "binoculars_used": true,
              "combined_score": 0.248051339913131,
              "confidence": 0.248051339913131,
              "content_id": "c_ea2e14f31109",
              "creator_id": "eval_c1c9f55f_c5_t3_own_1",
              "guess": "human",
              "label": "human",
              "label_text": "Our checks  suggest this text was written by a person. This assessment can be wrong.",
              "model_score": 0.0853,
              "perplexity_score": 0.1592,
              "status": "decided",
              "style_score": 0.6278044663771033,
              "timestamp": "2026-11-12T11:05:10+00:00",
              "word_count": 101
            }
          ],
          "audit_count_before": 646,
          "audit_count_after": 647,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "required_fields": true,
            "response_matches": true,
            "confidence_matches_combined": true,
            "decided": true
          }
        },
        {
          "id": "ai_00000113_00",
          "authorship": "ai",
          "expected_label": "ai",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "Certain sounds can be irritating to some people because they have a high frequency or because they are loud. High-pitched sounds, like the sound of metal scraping or a squeaking on a whiteboard, can be especially annoying because they are at a frequency that is particularly noticeable to the human ear. Some people may also find loud noises to be irritating, especially if they are sudden or unexpected. It's also possible that some people simply have a lower tolerance for certain sounds, whether they are high-pitched or loud, and find them more irritating than others do.",
              "creator_id": "eval_c1c9f55f_c5_t3_ai_00000113_00"
            },
            "sent_at_utc": "2026-11-12T11:05:10.183318+00:00",
            "status": 200,
            "response": {
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_6a52ee625da8",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "style_score": 0.5755367883306223
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:10.289239+00:00",
            "duration_seconds": 0.1059347920017899
          },
          "audit_entries": [
            {
              "binoculars_score": 0.9584,
              "binoculars_used": false,
              "combined_score": 0.7923010364991867,
              "confidence": 0.7923010364991867,
              "content_id": "c_6a52ee625da8",
              "creator_id": "eval_c1c9f55f_c5_t3_ai_00000113_00",
              "guess": "ai",
              "label": "ai",
              "label_text": "Our checks suggest this text may have been generated by AI. This assessment can be wrong, and the writer can request a review.",
              "model_score": 0.8852,
              "perplexity_score": 0.8852,
              "status": "decided",
              "style_score": 0.5755367883306223,
              "timestamp": "2026-11-12T11:05:10+00:00",
              "word_count": 96
            }
          ],
          "audit_count_before": 647,
          "audit_count_after": 648,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "required_fields": true,
            "response_matches": true,
            "confidence_matches_combined": true,
            "decided": true
          }
        },
        {
          "id": "empty_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": "eval_c1c9f55f_c5_t3_empty_text"
            },
            "sent_at_utc": "2026-11-12T11:05:10.309708+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:10.311935+00:00",
            "duration_seconds": 0.0022305410020635463
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t3_empty_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:05:10+00:00"
            }
          ],
          "audit_count_before": 648,
          "audit_count_after": 649,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "missing_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "creator_id": "eval_c1c9f55f_c5_t3_missing_text"
            },
            "sent_at_utc": "2026-11-12T11:05:10.328555+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:05:10.330749+00:00",
            "duration_seconds": 0.002194041997427121
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t3_missing_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:05:10+00:00"
            }
          ],
          "audit_count_before": 649,
          "audit_count_after": 650,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "list_text",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": [
                "not",
                "a",
                "string"
              ],
              "creator_id": "eval_c1c9f55f_c5_t3_list_text"
            },
            "sent_at_utc": "2026-11-12T11:06:10.896185+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:06:10.900191+00:00",
            "duration_seconds": 0.004009999996924307
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "eval_c1c9f55f_c5_t3_list_text",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:06:10+00:00"
            }
          ],
          "audit_count_before": 650,
          "audit_count_after": 651,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "null_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": null
            },
            "sent_at_utc": "2026-11-12T11:06:10.937082+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:06:10.940150+00:00",
            "duration_seconds": 0.003074874999583699
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": null,
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:06:10+00:00"
            }
          ],
          "audit_count_before": 651,
          "audit_count_after": 652,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "empty_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": ""
            },
            "sent_at_utc": "2026-11-12T11:06:10.971125+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:06:10.973584+00:00",
            "duration_seconds": 0.0024645410012453794
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:06:10+00:00"
            }
          ],
          "audit_count_before": 652,
          "audit_count_after": 653,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "whitespace_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": "   "
            },
            "sent_at_utc": "2026-11-12T11:06:11.002779+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:06:11.004906+00:00",
            "duration_seconds": 0.0021273329984978773
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "   ",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:06:11+00:00"
            }
          ],
          "audit_count_before": 653,
          "audit_count_after": 654,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "object_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": "",
              "creator_id": {
                "name": "invalid"
              }
            },
            "sent_at_utc": "2026-11-12T11:06:11.031727+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:06:11.033909+00:00",
            "duration_seconds": 0.002184832999773789
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": {
                "name": "invalid"
              },
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:06:11+00:00"
            }
          ],
          "audit_count_before": 654,
          "audit_count_after": 655,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": false,
            "controlled_rejection": true,
            "rejection_format": true
          }
        },
        {
          "id": "missing_creator",
          "submission": {
            "method": "POST",
            "url": "http://127.0.0.1:5000/submit",
            "request": {
              "text": ""
            },
            "sent_at_utc": "2026-11-12T11:06:11.054964+00:00",
            "status": 400,
            "response": {
              "error": "bad_request",
              "message": "Send JSON with a non-empty \"text\"."
            },
            "error": null,
            "received_at_utc": "2026-11-12T11:06:11.056677+00:00",
            "duration_seconds": 0.0017130000051110983
          },
          "audit_entries": [
            {
              "combined_score": null,
              "content_id": null,
              "creator_id": "unknown",
              "event": "rejected",
              "guess": null,
              "http_status": 400,
              "label": null,
              "model_score": null,
              "reason": "missing_or_invalid_text",
              "status": "rejected",
              "style_score": null,
              "timestamp": "2026-11-12T11:06:11+00:00"
            }
          ],
          "audit_count_before": 655,
          "audit_count_after": 656,
          "checks": {
            "one_entry": true,
            "timestamp": true,
            "creator_id": true,
            "controlled_rejection": true,
            "rejection_format": true
          }
        }
      ]
    }
  ]
}
```
