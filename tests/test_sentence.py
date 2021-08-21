from duo3.sentence import Sentences


def test_sentences(sentences: Sentences):
    assert len(sentences) == 560
    assert sentences[0].english.startswith("We must respect")
    assert list(sentences.noiter(1)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for no in sentences.noiter([2, 5]):
        assert 10 <= no <= 21 or 46 <= no <= 62


def test_sample(sentences: Sentences):
    x = sentences.sample(3, 5)
    assert len(x) == 5
    for s in x:
        assert 22 <= s.no <= 35
    x = sentences.sample(3, 0)
    assert len(x) == 14
