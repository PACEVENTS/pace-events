#!/usr/bin/env python3
"""YouthConnekt Africa Summit 2026 (25-27 Nov 2026, KCC Kigali).
Sessions/times/rooms: official programme PDF dated 22.11.26.
Speakers: YCA_Summit_2026_Session_Tracker (Google Drive), CONFIRMED speakers only, no placeholders.
Session ids double as Otter title codes (D1-01 ...)."""
import json, re, secrets, string, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
T = json.load(open('/home/claude/yca/tracker_sessions.json'))
D1, D2, D3 = '2026-11-25', '2026-11-26', '2026-11-27'
BAD = re.compile(r'^(CEO|To be identified|Self-facilitated|Session will|Final youth|Youth speaker \d|Ministers Roundtable|.*representative$)', re.I)

def spk(*idx):
    out = []
    for i in idx:
        for p in T[i]['speakers']:
            if p['status'] != 'Confirmed': continue
            lines = [l.strip(' ,') for l in str(p['name']).split('\n') if l.strip(' ,')]
            if not lines or BAD.match(lines[0]): continue
            name, rest = lines[0], ', '.join(lines[1:])
            m = re.match(r'^(.*?),\s*(.+)$', name) if not rest and ',' in name and len(name) > 40 else None
            if m: name, rest = m.group(1), m.group(2)
            name = re.sub(r'\b(Mr|Ms|Mrs|Dr|Hon)\.(?=\S)', r'\1. ', name)
            r2 = p['role'] if p['role'] not in (None, 'Speaker', 'Panellist') else ''
            if r2 and r2.lower().rstrip('s') in rest.lower(): r2 = ''
            if rest.lower().rstrip('s') == r2.lower(): rest = ''
            role = ', '.join(x for x in [rest, r2] if x)
            if role.lower() in ('mcs', 'mc'): role = 'MC'
            for n in re.split(r'\s+&\s+', name) if '&' in name and len(name) < 60 else [name]:
                out.append({'name': n.strip(), 'role': role})
    return out

S = []
def add(id, day, st, en, title, room='', kind='', speakers=(), closed=False, plain=False, time_label=None):
    S.append({'id': id, 'day': day, 'start': st, 'end': en, 'sort': st + id[-2:], 'timeLabel': time_label, 'room': room,
              'title': title, 'kind': '' if plain else kind, 'closed': closed,
              'speakers': [] if plain else list(speakers), 'transcript': False})
ZONES = 'Health Corner · Connekting Zone · AUC Egumeni Hub (AD10)'

# Day 1
add('d1-arrival', D1, '08:30', '10:30', 'Arrival of delegates · Networking & DJ', plain=True)
add('d1-01', D1, '11:00', '12:30', 'Official Opening Ceremony', 'Auditorium', 'High-level plenary', spk(13))
add('d1-02', D1, '11:00', '12:30', 'Generational Xchange: "Shaping the Generational Mission"', 'Auditorium', 'Conversation with Heads of State', spk(14))
add('d1-launch', D1, '11:00', '12:30', 'Launch of Youth Spaces · Youth Innovations Marketplace', plain=True)
add('d1-lunch', D1, '13:00', '14:00', 'Lunch', plain=True)
add('d1-03', D1, '14:30', '16:00', 'Passing the Torch: Civic Action Across Generations', 'Auditorium', 'Cine debate · ASG', spk(16))
add('d1-04', D1, '14:30', '16:00', "Africa's Turn: Unlocking Opportunities Within, Shaping the World Beyond", 'MH3', 'TED talk style · YCA Hub', spk(17))
add('d1-05', D1, '14:30', '16:00', 'Policy Roundtable on Climate Change and SRHR', 'AD12', 'Policy roundtable · UNFPA, AUC, Imbuto Foundation', spk(18))
add('d1-zones', D1, '14:30', '16:00', ZONES, plain=True)
add('d1-gala', D1, '18:00', '20:30', 'Gala Dinner (hosted by the Government of Rwanda)', '', 'By invitation', closed=True)
add('d1-film', D1, '18:00', '20:00', 'Kigali Immersion: Outdoor Film Screening (Mashariki Film Festival) · KCC Roundabout', plain=True)
add('d1-zaria', D1, '18:00', '20:00', 'Kigali Immersion: Imagine Kigali Day · Zaria Court', plain=True)
add('d1-unipod', D1, '18:00', '20:00', 'UNIPOD Demo Evening & Social Mixer (UNDP) · UNIPOD UR-CST', '', 'By invitation', closed=True)
# Day 2
add('d2-arrival', D2, '08:30', '09:30', 'Arrival of delegates · Networking & DJ', plain=True)
add('d2-01', D2, '08:30', '09:30', "Securing the Future of Africa's University Innovation Pods", 'AD10', 'Ministerial breakfast · UNDP · By invitation', closed=True)
add('d2-02', D2, '09:30', '11:00', 'The Future of Jobs', 'Auditorium', 'TED talk & interactive panel · UNDP', spk(28))
add('d2-03', D2, '09:30', '11:00', 'Beyond the City: Building Resilient Livelihoods 4 Rural Young Women (Part 1)', 'MH2', 'Workshop · BRAC', spk(29))
add('d2-04', D2, '11:30', '13:00', 'Buy from Youth: Turning Green Livelihoods into Green Markets', 'Auditorium', 'High-level interactive panel · FAO, WFP, AGRA', spk(30))
add('d2-05', D2, '11:30', '13:00', 'Thrive Africa: Investing in Innovative Youth Health, Education & Empowerment', 'MH1', 'Intergenerational fireside chat · UNFPA, Imbuto Foundation, AU', spk(31))
add('d2-06', D2, '11:30', '13:00', 'Beyond the City: Building Resilient Livelihoods 4 Rural Young Women (Part 2)', 'MH2', 'Workshop · BRAC', spk(32))
add('d2-07', D2, '11:30', '13:00', 'Influencing the Change: Youth Leadership in Africa', 'MH3', 'TED talk · YAC', spk(33))
add('d2-08', D2, '11:30', '13:00', 'Green Opportunity Lab: Bassin du Congo', 'AD12', 'Workshop · YC Bassin du Congo', spk(34))
add('d2-09', D2, '11:30', '13:00', 'Young Africans Shaping Safe and Inclusive Digital Futures', 'AD10', 'Workshop · AUC, UN Women', spk(35))
add('d2-lunch', D2, '13:00', '14:00', 'Lunch', plain=True)
add('d2-10', D2, '14:30', '16:00', 'Reimagining African Creativity', 'Auditorium', 'Generational debate', spk(39, 40))
add('d2-11', D2, '14:30', '16:00', 'YouthConnektXRegions', 'MH1', 'Learning spotlight · YC Mano River Union & Sahel Regional Forum', spk(44))
add('d2-12', D2, '14:30', '16:00', 'Making Finance Work for Rural Youth Enterprises', 'MH2', 'Learning spotlight & youth fireside · CRS', spk(41))
add('d2-13', D2, '14:30', '16:00', 'ACET Youth Policy Lab', 'MH3', 'Policy lab · ACET', spk(42))
add('d2-14', D2, '14:30', '16:00', 'Policy Roundtable on Inclusive Trade', 'AD12', 'Roundtable · YCA Hub, UNDP', spk(43))
add('d2-zones', D2, '14:30', '16:00', ZONES, plain=True)
add('d2-talent', D2, '17:30', '19:30', 'Youth Talent Night · Auditorium', plain=True)
# Day 3
add('d3-arrival', D3, '08:30', '09:30', 'Arrival of delegates · Networking & DJ', plain=True)
add('d3-01', D3, '08:30', '10:00', 'Secondary Education in Africa (SEA) Report Launch', 'AD10', 'High-level breakfast · Mastercard Foundation · By invitation', closed=True)
add('d3-02', D3, '09:30', '11:00', 'Legacy vs NextGen: the Future of Sports Economy', 'Auditorium', 'Generational debate · YCA Hub, MINISPORTS', spk(48))
add('d3-03', D3, '11:30', '13:00', 'Trajectories of Dignified Employment', 'Auditorium', 'High-level session · Mastercard Foundation', spk(49))
add('d3-04', D3, '11:30', '13:00', 'YouthConnekt Southern Africa: Pitch Your Country', 'MH1', 'Generational debate · YouthConnekt Zambia, UNDP ECoWYERT', spk(51))
add('d3-05', D3, '11:30', '13:00', 'The Next Tech Africa Giants', 'MH2', 'TED talk & interactive panel · Smart Africa', spk(50))
add('d3-06', D3, '11:30', '13:00', "Africa's Creative Wealth: Creatives4Peace", 'MH3', 'TED talk · UNDP', spk(52))
add('d3-07', D3, '11:30', '13:00', 'YouthConnekt Mano River Union Steering Committee Meeting', 'AD12', 'Boardroom · By invitation', closed=True)
add('d3-zones', D3, '11:30', '13:00', ZONES, plain=True)
add('d3-lunch', D3, '13:00', '14:00', 'Lunch', plain=True)
add('d3-08', D3, '14:30', '16:00', 'Official Closing Ceremony', 'Auditorium', 'Plenary')

existing = sorted(REPO.glob('data/youthconnekt-africa-2026-*'))
slug = existing[0].name if existing else 'youthconnekt-africa-2026-' + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
d = REPO / 'data' / slug
(d / 'transcripts').mkdir(parents=True, exist_ok=True)
prog = {'timezoneLabel': 'Kigali time (GMT +02:00)',
        'days': [{'date': D1, 'label': 'Day 1'}, {'date': D2, 'label': 'Day 2'}, {'date': D3, 'label': 'Day 3'}],
        'sessions': S}
old = d / 'program.json'
if old.exists():  # keep transcript flags already published
    have = {s['id'] for s in json.loads(old.read_text())['sessions'] if s.get('transcript')}
    for s in S: s['transcript'] = s['id'] in have
old.write_text(json.dumps(prog, ensure_ascii=False, indent=2))
(d / 'event.json').write_text(json.dumps({
    'slug': slug, 'name': 'YouthConnekt Africa Summit 2026', 'short': "YCA '26",
    'startDate': D1, 'endDate': D3, 'venue': 'Kigali Convention Centre, Kigali',
    'logo': 'assets/yca-2026-logo.png', 'accent': '#ED592A', 'ink': '#035E4D',
    'driveTranscriptFolder': '1Df1TXRWkAEqBqKbOhllHPNAujToYBcL0'}, ensure_ascii=False, indent=2))
print(slug, len(S), 'items')
for s in S:
    if not s['kind'] or s['closed']: continue
    print(f"  {s['id'].upper():6s} {s['start']} {s['room']:10s} spk={len(s['speakers']):2d}  {s['title'][:60]}")
