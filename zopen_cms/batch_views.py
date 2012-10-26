# -*- encoding:utf-8 -*-

""" 分页 """

from pyramid.renderers import render

def batch_view(batch, request):
    kss_next_number = 0
    next_url = ''
    previous_url = ''
    kss_previous_number = 0
   
    batch_start = request.params.get('b_start', '0')
    if batch_start.endswith('/'): 
        batch_start = batch_start[:-1]
    batch_start = int(batch_start)

    batch_size = batch.size
    batch_total = batch.total
    if batch.previous:
        previous_url = item_url(request, batch.previous.start)
        kss_previous_number = batch.previous.start
    if batch.next:
        next_url = item_url(request, batch.next.start)
        if batch.next.start:
            kss_next_number = batch.next.start

    count = 0
    previous_batchs = []
    mybatch = batch
    while mybatch.previous:
        count = count + 1
        if count > 2:
            break
        previous_batchs.append(mybatch.previous)
        mybatch = mybatch.previous
    previous_batchs.reverse()
        
    count = 0
    next_batchs = []
    mybatch = batch
    while mybatch.next:
        count = count + 1
        if count > 2:
            break
        next_batchs.append(mybatch.next)
        mybatch = mybatch.next
    
    last_batch = None
    if batch.total-2 > batch.number:
        last_batch = batch.batches[batch.total-1]

    first_batch = None
    if batch.number-2 > 1:
        first_batch = batch.batches[0]

    return render(
        'templates/batch.pt',
        dict(
            batch = batch,
            batch_total = batch_total,
            previous_url = previous_url,
            kss_previous_number = kss_previous_number,
            batch_size = batch_size,
            kss_next_number = kss_next_number,
            next_url = next_url,
            first_batch = first_batch,
            previous_batchs = previous_batchs,
            next_batchs = next_batchs,
            last_batch = last_batch,
        )
    )

def item_url(request, b_start):
    page_url = str(request.url).split('?')[0]
    if len(request.params) == 0 or \
      (len(request.params) == 1 and 'b_start' in request.params):
        item_url = '%s?b_start=%s' % (page_url, str(b_start))
    else:
        if 'b_start' in request.params:
            del request.params[0]
        key = request.params.keys()[0]
        item_url = '%s?%s=%s' % (page_url, key, request.params.get(key))
        for key in request.params.keys()[1:]:
            item_url = item_url + '&%s=%s' % (key, request.params.get(key))
        item_url = item_url + '&b_start=' + str(b_start)
    return item_url


