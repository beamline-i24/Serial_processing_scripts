
def client_calculator(np_array, compare, args):
    spot_count_cutoff = args.spot_count_cutoff
    high_spot_min = 2
    intensity_min = 0
    #intensity_max = 0
    noise1_min = 0
    noise1_max = 0.82
    noise2_min = 0
    noise2_max = 0.96
    hit_count=0
    hit_images = []
    for num, i, hit, strong, high, noise_1, noise_2, d_min, d_min_1, d_min_2 in np_array:
        if compare:
           if hit > 0:
              if strong < spot_count_cutoff:
                 print 'ssstrong'
                 print num, i, hit, strong, high, noise_1, noise_2
              elif i < 0:
                 print'intensity'
                 print num, i, hit, strong, high, noise_1, noise_2
              elif noise_1 < 0 or noise_1 >0.82:
                 print'noise'
                 print num, i, hit, strong, high, noise_1, noise_2
              elif noise_2 < 0 or noise_2 >0.96:
                 print'noise 22222222222'
                 print num, i, hit, strong, high, noise_1, noise_2
              elif high < 2:
                 print'high'
                 print num, i, hit, strong, high, noise_1, noise_2
        if strong >= spot_count_cutoff:
          if i >= 0:
             if  0.0 <= noise_1 <= 0.82:
                if 0.0 <= noise_2 <= 0.96:
                   if high >= 2:
                      hit_count+=1
                      hit_images.append([num, hit])
        return hit_count, hit_images
